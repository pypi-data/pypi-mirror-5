<%! import jsonrpc.jsonutil %>
<%inherit file="/page" />

<%
filesize = sum([(bdo.get('filesize') or 0) for bdo in bdos])
%>

<%block name="js_ready">
    ${parent.js_ready()}
    $("#e2-download").DownloadControl({});
</%block>


<form id="e2-download" method="post" action="${ctxt.root}/download/">
    <input type="hidden" name="tar" value="True" />
    <h1>
        <span class="e2-download-filecount">${len(bdos)}</span> files, <span class="e2-download-filesize">${filesize}</span>

        <ul class="e2l-actions">
            <li><input type="submit" value="Download selected attachments" /></li>
            <li>
                <input type="checkbox" name="rename" value="name" id="e2-download-rename" />
                <label for="e2-download-rename">Add attachment ID to filenames</label>
            </li>
        </ul>
    </h1>

    <table class="e2l-shaded">
        <thead>
            <tr>
                <th><input type="checkbox" checked="checked" class="e2-download-allbids" value="" /></th>
                <th>Filename</th>
                <th>Size</th>
                <th>Record</th>
                <th>Creator</th>
                <th>Created</th>
            </tr>
        </thead>

        <tbody>
        % for bdo in bdos:
            <tr>
                <td><input type="checkbox" checked="checked" name="bids" value="${bdo.name}" data-filesize="${bdo.get('filesize',0)}" /></td>
                <td>
                    <%
                    ## Grumble...
                    fn = bdo.filename
                    try:
                        if isinstance(fn, str):
                            fn = bdo.filename.decode('utf-8')
                    except:
                        fn = bdo.name
                    %>
                    <a href="${ctxt.root}/download/${bdo.name}/${fn}">
                        <img class="e2l-thumbnail" src="${ctxt.root}/download/${bdo.name}/thumb.jpg?size=thumb" alt="" /> 
                        ${fn}
                    </a>
                </td>
                <td class="e2-download-filesizes" data-filesize="${bdo.get('filesize',0)}">${bdo.get('filesize',0)}</td>
                <td><a href="${ctxt.root}/record/${bdo.record}/">${recnames.get(bdo.record)}</a></td>
                <td><a href="${ctxt.root}/user/${bdo.get('creator')}/">${users_d.get(bdo.get('creator'), dict()).get('displayname')}</a></td>
                <td><time class="e2-localize" datetime="${bdo.get('creationtime')}">${bdo.get('creationtime')}</time></td>
            </tr>
        % endfor
        </tbody>

    </table>


</form>
