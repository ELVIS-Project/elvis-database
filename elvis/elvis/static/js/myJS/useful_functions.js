/*
* Creates an overlay/popup. Must specify .popup and .overlay in css styles 
* Example arguments: 25%, 25%, 300px, 400px, invite. 
* This creates a 300x400px popup containing html page found at /current/location/invite, 25% from left and 25% from top. 
*/
function expand(left, top, width, height, toLoad){
	// Create background overlay 
	var overlay = document.createElement("div");
	overlay.setAttribute("class", "overlay");
	overlay.setAttribute("id", "overlay");
	document.body.appendChild(overlay);
	// Create the popup box
	var popup = document.createElement("div");
	popup.setAttribute("class", "popup");
	popup.style.top = top;
	popup.style.left = left;
	popup.style.width = width;
	popup.style.height = height;
	document.body.appendChild(popup);
	// Append predefined html invite users page to this div
	$(".popup").load(toLoad);
}

/*
* Closes popup and removes overlay (these must be specified in css). 
*/
function close() {
	document.body.removeChild(document.getElementById("overlay"));
	document.body.removeChild(document.getElementById("popup"));
}

/*
* Highlights elements according to a color (red or green) 
*/
function highlight(id, color) {
	var id_num = id.match(/\d+$/)[0];
	var cell_name = "tag-cell-name"+id_num;
	var cell_opt = "tag-cell-opt"+id_num;

	var curr_background = document.getElementById(cell_name).style.background;

	// Check if background color has already been set. If so, unset and return
	if( curr_background == "rgb(144, 238, 144)" || curr_background == "rgb(250, 128, 114)" ) {
		document.getElementById(cell_name).style.background = "none";
		document.getElementById(cell_opt).style.background = "none";
		// Now need to delete it from array 
		var index = clicked_name.indexOf(cell_name)-1;
		clicked_name.splice(index, 1);
		clicked_opt.splice(index, 1);
		colors.splice(index, 1);
	}

	else {
		clicked_name.push(cell_name);
		clicked_opt.push(cell_opt);
		colors.push(color);

		// Set new colors
		for (intI=0; intI<colors.length; intI++) {
			document.getElementById(clicked_name[intI]).style.background = colors[intI];
			document.getElementById(clicked_opt[intI]).style.background = colors[intI];
		}
	}
}
