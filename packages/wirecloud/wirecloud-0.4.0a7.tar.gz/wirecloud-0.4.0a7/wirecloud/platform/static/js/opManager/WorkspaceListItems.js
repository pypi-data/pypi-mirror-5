/*
 *     (C) Copyright 2012 Universidad Politécnica de Madrid
 *
 *     This file is part of Wirecloud Platform.
 *
 *     Wirecloud Platform is free software: you can redistribute it and/or
 *     modify it under the terms of the GNU Affero General Public License as
 *     published by the Free Software Foundation, either version 3 of the
 *     License, or (at your option) any later version.
 *
 *     Wirecloud is distributed in the hope that it will be useful, but WITHOUT
 *     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 *     FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
 *     License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with Wirecloud Platform.  If not, see
 *     <http://www.gnu.org/licenses/>.
 *
 */

/*jshint forin:true, eqnull:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true, undef:true, curly:true, browser:true, indent:4, maxerr:50 */
/*global OpManagerFactory, StyledElements*/

var WorkspaceListItems = function (handler, options) {
    StyledElements.DynamicMenuItems.call(this);

    this.handler = handler;
};
WorkspaceListItems.prototype = new StyledElements.DynamicMenuItems();

WorkspaceListItems.prototype.build = function () {
    var workspace_keys, i, items, workspace;

    items = [];

    workspace_keys = OpManagerFactory.getInstance().workspaceInstances.keys();
    for (i = 0; i < workspace_keys.length; i += 1) {
        workspace = OpManagerFactory.getInstance().workspaceInstances.get(workspace_keys[i]);

        items.push(new StyledElements.MenuItem(
            workspace.getName(),
            this.handler.bind(this, workspace)
        ));
    }

    return items;
};
