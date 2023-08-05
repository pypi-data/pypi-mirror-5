<%! 
import jsonrpc.jsonutil
%>

<%inherit file="/pages/home" />
<%namespace name="buttons" file="/buttons"  /> 
<%namespace name="user_util" file="/pages/user"  /> 


<%block name="js_ready">
    ${parent.js_ready()}
    ## Recent activity viewer
    var q = ${recent_activity | n,jsonencode};
    $('#recent_activity').PlotHistogram({
        q:q,
        pan: false,
        height:200,
    });
</%block>


## <h1>
##    ${USER.displayname}
##    <a class="e2l-hact e2-button" href="${ctxt.root}/user/${USER.name}/edit/"><img src="${ctxt.root}/static/images/edit.png" alt="Edit" /> Edit Profile</a>
## </h1>
## <div class="e2l-cf">
##    ${user_util.profile(user=USER, userrec=USER.userrec, edit=False)}
## </div>
## <br /><br />


% if banner:
    <h1>
        Welcome to ${TITLE}
        % if banner.writable():
            <a class="e2l-hact e2-button e2-record e2-record-edit" data-name="${banner.name}" href="${ctxt.root}/record/${banner.name}#edit">${buttons.image('edit.png')} Edit</a>
        % endif
    </h1>
    <div class="e2l-cf">
        ${render_banner | n,unicode}
    </div>
    <br /><br />
% endif




<h1>
    Activity and recent records
    <a class="e2l-hact e2-button" href="${ctxt.root}/records/">Record tree</a>
    <a class="e2l-hact e2-button" href="${ctxt.root}/query/">All records</a>
</h1>

<div id="recent_activity">
    <div class="e2-plot"></div>
</div>

## ${unicode(recent_activity_table) | n}

<br /><br />




% for group in groups:
    <h1>
        <a href="${ctxt.root}/record/${group.name}/" id="groups-${group.name}">
        	${recnames.get(group.name, group.name)}
		</a>
            % if group.writable():
                <a class="e2l-hact e2-button e2-record-new" href="${ctxt.root}/record/${group.name}/new/project/" data-parent="${group.name}" data-rectype="project">${buttons.image('new.png')} New</a>
            % endif
            ## <a class="e2l-hact e2-button" href="${ctxt.root}/record/${group.name}/children/project/">View projects in table</a>
    </h1>
    
    <ul class="e2l-sidebar-projectlist">
        % if not groups_children.get(group.name):
            <li>No projects</li>
        % endif
        % for project in sorted(groups_children.get(group.name, []), key=lambda x:recnames.get(x, '').lower()):
            <li>
                <a href="${ctxt.root}/record/${project}/">
                    ${recnames.get(project, project)}
                </a>
                <span class="e2l-shadow e2l-sidebar-count">
                    ${len(projects_children.get(project, [])) or ''}                        
                </span>
                </li>
        % endfor
    </ul>
    
    <br /><br /><br /><br />
% endfor


