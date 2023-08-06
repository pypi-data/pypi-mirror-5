import reikna.helpers as helpers
from reikna.cluda import Module, Snippet


VALUE_NAME = "_val"
INDEX_NAME = "_idx"


def leaf_name(name):
    return "_leaf_" + name


def index_cnames(shape):
    return [INDEX_NAME + str(i) for i in range(len(shape))]


def index_cnames_str(param, qualified=False):
    names = index_cnames(param.annotation.type.shape)
    if qualified:
        names = ["VSIZE_T " + name for name in names]
    return ", ".join(names)


def flat_index_expr(param):
    # FIXME: Assuming that all strides are multiples of dtype.itemsize,
    # which is true as long as we use primitive types from numpy.
    # This can change with custom structures, and we will have
    # to cast device pointer to bytes and back.
    # Need to investigate what happens in this case on some concrete example.

    type_ = param.annotation.type
    item_strides = [stride // type_.dtype.itemsize for stride in type_.strides]

    names = index_cnames(param.annotation.type.shape)

    return " + ".join([
        name + " * " + str(stride)
        for name, stride in zip(names, item_strides)])


def param_cname(param, qualified=False):
    name = "_leaf_" + param.name
    if qualified:
        ctype = param.annotation.type.ctype
        if param.annotation.array:
            return "GLOBAL_MEM " + ctype + " *" + name
        else:
            return ctype + " " + name
    else:
        return name


def param_cnames_str(parameters, qualified=False):
    return ", ".join([param_cname(p, qualified=qualified) for p in parameters])


def kernel_declaration(kernel_name, parameters):
    return "KERNEL void {kernel_name}({cnames_str})".format(
        kernel_name=kernel_name, cnames_str=param_cnames_str(parameters, qualified=True))


def node_connector(output):
    if output:
        return VALUE_NAME
    else:
        return VALUE_NAME + " ="


_module_transformation = helpers.template_def(
    ['prefix'],
    """
    // ${'output' if output else 'input'} transformation node for "${name}"
    INLINE WITHIN_KERNEL ${'void' if output else connector_ctype} ${prefix}func(
        ${q_params},
        ${q_indices}
        %if output:
        , ${connector_ctype} ${VALUE_NAME}
        %endif
        )
    {
        %if not output:
        ${connector_ctype} ${VALUE_NAME};
        %endif

        ${tr_snippet(*tr_args)}

        %if not output:
        return ${VALUE_NAME};
        %endif
    }
    %if output:
    #define ${prefix}(${nq_indices}, ${VALUE_NAME}) ${prefix}func(\\
        ${nq_params}, ${nq_indices}, ${VALUE_NAME})
    %else:
    #define ${prefix}(${nq_indices}) ${prefix}func(${nq_params}, ${nq_indices})
    %endif
    """)

def module_transformation(output, param, subtree_parameters, tr_snippet, tr_args):
    return Module(
        _module_transformation,
        render_kwds=dict(
            output=output,
            name=param.name,
            q_params=param_cnames_str(subtree_parameters, qualified=True),
            q_indices=index_cnames_str(param, qualified=True),
            VALUE_NAME=VALUE_NAME,
            nq_params=param_cnames_str(subtree_parameters),
            nq_indices=index_cnames_str(param),
            connector_ctype=param.annotation.type.ctype,
            tr_snippet=tr_snippet,
            tr_args=tr_args))


_module_leaf_macro = helpers.template_def(
    ['prefix'],
    """
    // leaf ${'output' if output else 'input'} macro for "${name}"
    %if output:
    #define ${prefix}(${index_str}, ${VALUE_NAME}) ${lname}[${index_expr}] = (${VALUE_NAME})
    %else:
    #define ${prefix}(${index_str}) (${lname}[${index_expr}])
    %endif
    """)

def module_leaf_macro(output, param):
    return Module(
        _module_leaf_macro,
        render_kwds=dict(
            output=output,
            name=param.name,
            VALUE_NAME=VALUE_NAME,
            lname=leaf_name(param.name),
            index_str=index_cnames_str(param),
            index_expr=flat_index_expr(param)))


_module_same_indices = helpers.template_def(
    ['prefix'],
    """
    // ${'output' if output else 'input'} for a transformation for "${name}"
    %if output:
    #define ${prefix}(${VALUE_NAME}) ${module_idx}(${nq_indices}, ${VALUE_NAME})
    %else:
    #define ${prefix} ${module_idx}(${nq_indices})
    %endif
    """)

def module_same_indices(output, param, subtree_parameters, module_idx):
    return Module(
        _module_same_indices,
        render_kwds=dict(
            output=output,
            name=param.name,
            VALUE_NAME=VALUE_NAME,
            module_idx=module_idx,
            nq_indices=index_cnames_str(param),
            nq_params=param_cnames_str(subtree_parameters)))


_snippet_disassemble_combined = Snippet.create(
    lambda shape, slices, indices, combined_indices: """
    %for combined_index, slice_len in enumerate(slices):
    <%
        index_start = sum(slices[:combined_index])
        index_end = index_start + slice_len
    %>
        %for index in range(index_start, index_end):
        <%
            stride = product(shape[index+1:index_end])
        %>
        VSIZE_T ${indices[index]} = ${combined_indices[combined_index]} / ${stride};
        ${combined_indices[combined_index]} -= ${indices[index]} * ${stride};
        %endfor
    %endfor
    """,
    render_kwds=dict(product=helpers.product))

_module_combined = helpers.template_def(
    ['prefix', 'slices'],
    """
    <%
        combined_indices=['_c_idx' + str(i) for i in range(len(slices))]
        q_combined_indices=", ".join(['VSIZE_T ' + ind for ind in combined_indices])
        nq_combined_indices=", ".join(combined_indices)
    %>
    INLINE WITHIN_KERNEL ${'void' if output else connector_ctype} ${prefix}func(
        ${q_params},
        ${q_combined_indices}
        %if output:
        , ${connector_ctype} ${VALUE_NAME}
        %endif
        )
    {
        ${disassemble(shape, slices, indices, combined_indices)}
        %if output:
        ${module_idx}(${nq_indices}, ${VALUE_NAME});
        %else:
        return ${module_idx}(${nq_indices});
        %endif
    }
    %if output:
    #define ${prefix}(${nq_combined_indices}, ${VALUE_NAME}) ${prefix}func(\\
        ${nq_params}, ${nq_combined_indices}, ${VALUE_NAME})
    %else:
    #define ${prefix}(${nq_combined_indices}) ${prefix}func(\\
        ${nq_params}, ${nq_combined_indices})
    %endif
    """)

def module_combined(output, param, subtree_parameters, module_idx):
    return Module(
        _module_combined,
        render_kwds=dict(
            output=output,
            VALUE_NAME=VALUE_NAME,
            shape=param.annotation.type.shape,
            module_idx=module_idx,
            disassemble=_snippet_disassemble_combined,
            connector_ctype=param.annotation.type.ctype,
            nq_indices=index_cnames_str(param),
            q_indices=index_cnames_str(param, qualified=True),
            q_params=param_cnames_str(subtree_parameters, qualified=True),
            nq_params=param_cnames_str(subtree_parameters),
            indices=index_cnames(param.annotation.type.shape)))
