# XSLT extension elements

cdef class XSLTExtension:
    u"""Base class of an XSLT extension element.
    """
    def execute(self, context, self_node, input_node, output_parent):
        u"""execute(self, context, self_node, input_node, output_parent)
        Execute this extension element.

        Subclasses must override this method.  They may append
        elements to the `output_parent` element here, or set its text
        content.  To this end, the `input_node` provides read-only
        access to the current node in the input document, and the
        `self_node` points to the extension element in the stylesheet.

        Note that the `output_parent` parameter may be `None` if there
        is no parent element in the current context (e.g. no content
        was added to the output tree yet).
        """
        pass

    def apply_templates(self, _XSLTContext context not None, node, output_parent=None,
                        *, elements_only=False, remove_blank_text=False):
        u"""apply_templates(self, context, node, output_parent=None, elements_only=False, remove_blank_text=False)

        Call this method to retrieve the result of applying templates
        to an element.

        The return value is a list of elements or text strings that
        were generated by the XSLT processor.  If you pass
        ``elements_only=True``, strings will be discarded from the result
        list.  The option ``remove_blank_text=True`` will only discard
        strings that consist entirely of whitespace (e.g. formatting).
        These options do not apply to Elements, only to bare string results.

        If you pass an Element as `output_parent` parameter, the result
        will instead be appended to the element (including attributes
        etc.) and the return value will be `None`.  This is a safe way
        to generate content into the output document directly, without
        having to take care of special values like text or attributes.
        Note that the string discarding options will be ignored in this
        case.
        """
        cdef xmlNode* c_parent
        cdef xmlNode* c_node
        cdef xmlNode* c_context_node
        assert context._xsltCtxt is not NULL, "XSLT context not initialised"
        c_context_node = _roNodeOf(node)
        #assert c_context_node.doc is context._xsltContext.node.doc, \
        #    "switching input documents during transformation is not currently supported"

        if output_parent is not None:
            c_parent = _nonRoNodeOf(output_parent)
        else:
            c_parent = tree.xmlNewDocNode(
                context._xsltCtxt.output, NULL, <unsigned char*>"fake-parent", NULL)

        c_node = context._xsltCtxt.insert
        context._xsltCtxt.insert = c_parent
        xslt.xsltProcessOneNode(
            context._xsltCtxt, c_context_node, NULL)
        context._xsltCtxt.insert = c_node

        if output_parent is not None:
            return None

        try:
            return self._collectXSLTResultContent(
                context, c_parent, elements_only, remove_blank_text)
        finally:
            # free all intermediate nodes that will not be freed by proxies
            tree.xmlFreeNode(c_parent)

    def process_children(self, _XSLTContext context not None, output_parent=None,
                         *, elements_only=False, remove_blank_text=False):
        u"""process_children(self, context, output_parent=None, elements_only=False, remove_blank_text=False)

        Call this method to process the XSLT content of the extension
        element itself.

        The return value is a list of elements or text strings that
        were generated by the XSLT processor.  If you pass
        ``elements_only=True``, strings will be discarded from the result
        list.  The option ``remove_blank_text=True`` will only discard
        strings that consist entirely of whitespace (e.g. formatting).
        These options do not apply to Elements, only to bare string results.

        If you pass an Element as `output_parent` parameter, the result
        will instead be appended to the element (including attributes
        etc.) and the return value will be `None`.  This is a safe way
        to generate content into the output document directly, without
        having to take care of special values like text or attributes.
        Note that the string discarding options will be ignored in this
        case.
        """
        cdef xmlNode* c_parent
        cdef xslt.xsltTransformContext* c_ctxt = context._xsltCtxt
        cdef xmlNode* c_old_output_parent = c_ctxt.insert
        assert context._xsltCtxt is not NULL, "XSLT context not initialised"

        # output_parent node is used for adding results instead of
        # elements list used in apply_templates, that's easier and allows to
        # use attributes added to extension element with <xsl:attribute>.

        if output_parent is not None:
            c_parent = _nonRoNodeOf(output_parent)
        else:
            c_parent = tree.xmlNewDocNode(
                context._xsltCtxt.output, NULL, <unsigned char*>"fake-parent", NULL)

        c_ctxt.insert = _nonRoNodeOf(output_parent)
        xslt.xsltApplyOneTemplate(c_ctxt,
            c_ctxt.node, c_ctxt.inst.children, NULL, NULL)
        c_ctxt.insert = c_old_output_parent

        if output_parent is not None:
            return None

        try:
            return self._collectXSLTResultContent(
                context, c_parent, elements_only, remove_blank_text)
        finally:
            # free all intermediate nodes that will not be freed by proxies
            tree.xmlFreeNode(c_parent)

    cdef _collectXSLTResultContent(self, _XSLTContext context, xmlNode* c_parent,
                                   bint elements_only, bint remove_blank_text):
        cdef xmlNode* c_node
        cdef xmlNode* c_next
        cdef _ReadOnlyProxy proxy
        cdef list results = [] # or maybe _collectAttributes(c_parent, 2) ?
        c_node = c_parent.children
        while c_node is not NULL:
            c_next = c_node.next
            if c_node.type == tree.XML_TEXT_NODE:
                if not elements_only:
                    s = funicode(c_node.content)
                    if not remove_blank_text or s.strip():
                        results.append(s)
                    s = None
            elif c_node.type == tree.XML_ELEMENT_NODE:
                proxy = _newReadOnlyProxy(
                    context._extension_element_proxy, c_node)
                results.append(proxy)
                # unlink node and make sure it will be freed later on
                tree.xmlUnlinkNode(c_node)
                proxy.free_after_use()
            else:
                raise TypeError, \
                    u"unsupported XSLT result type: %d" % c_node.type
            c_node = c_next
        return results


cdef _registerXSLTExtensions(xslt.xsltTransformContext* c_ctxt,
                             extension_dict):
    for ns_utf, name_utf in extension_dict:
        xslt.xsltRegisterExtElement(
            c_ctxt, _xcstr(name_utf), _xcstr(ns_utf),
            <xslt.xsltTransformFunction>_callExtensionElement)

cdef void _callExtensionElement(xslt.xsltTransformContext* c_ctxt,
                                xmlNode* c_context_node,
                                xmlNode* c_inst_node,
                                void* dummy) with gil:
    cdef _XSLTContext context
    cdef XSLTExtension extension
    cdef python.PyObject* dict_result
    cdef xmlNode* c_node
    cdef _ReadOnlyProxy context_node = None, self_node = None
    cdef object output_parent # not restricted to ro-nodes
    c_uri = _getNs(c_inst_node)
    if c_uri is NULL:
        # not allowed, and should never happen
        return
    if c_ctxt.xpathCtxt.userData is NULL:
        # just for safety, should never happen
        return
    context = <_XSLTContext>c_ctxt.xpathCtxt.userData
    try:
        try:
            dict_result = python.PyDict_GetItem(
                context._extension_elements, (<unsigned char*>c_uri, <unsigned char*>c_inst_node.name))
            if dict_result is NULL:
                raise KeyError, \
                    u"extension element %s not found" % funicode(c_inst_node.name)
            extension = <object>dict_result

            try:
                # build the context proxy nodes
                self_node = _newReadOnlyProxy(None, c_inst_node)
                if _isElement(c_ctxt.insert):
                    output_parent = _newAppendOnlyProxy(self_node, c_ctxt.insert)
                else:
                    # may be the document node or other stuff
                    output_parent = _newOpaqueAppendOnlyNodeWrapper(c_ctxt.insert)
                if c_context_node.type in (tree.XML_DOCUMENT_NODE,
                                           tree.XML_HTML_DOCUMENT_NODE):
                    c_node = tree.xmlDocGetRootElement(<xmlDoc*>c_context_node)
                    if c_node is not NULL:
                        context_node = _newReadOnlyProxy(self_node, c_node)
                    else:
                        context_node = None
                elif c_context_node.type in (tree.XML_ATTRIBUTE_NODE,
                                             tree.XML_TEXT_NODE,
                                             tree.XML_CDATA_SECTION_NODE):
                    # this isn't easy to support using read-only
                    # nodes, as the smart-string factory must
                    # instantiate the parent proxy somehow...
                    raise TypeError("Unsupported element type: %d" % c_context_node.type)
                else:
                    context_node  = _newReadOnlyProxy(self_node, c_context_node)

                # run the XSLT extension
                context._extension_element_proxy = self_node
                extension.execute(context, self_node, context_node, output_parent)
            finally:
                context._extension_element_proxy = None
                if self_node is not None:
                    _freeReadOnlyProxies(self_node)
        except Exception, e:
            try:
                e = unicode(e).encode(u"UTF-8")
            except:
                e = repr(e).encode(u"UTF-8")
            message = python.PyBytes_FromFormat(
                "Error executing extension element '%s': %s",
                c_inst_node.name, _cstr(e))
            xslt.xsltTransformError(c_ctxt, NULL, c_inst_node, message)
            context._exc._store_raised()
        except:
            # just in case
            message = python.PyBytes_FromFormat(
                "Error executing extension element '%s'", c_inst_node.name)
            xslt.xsltTransformError(c_ctxt, NULL, c_inst_node, message)
            context._exc._store_raised()
    except:
        # no Python functions here - everything can fail...
        xslt.xsltTransformError(c_ctxt, NULL, c_inst_node,
                                "Error during XSLT extension element evaluation")
        context._exc._store_raised()
