var state = 0;



function sping(firstid, secondid){
    var answer = ping(firstid,secondid);
    //display(answer);
    alert(answer);
};



function saddNode(xcor, ycor){
    var type;
    if(state == 1)
	type = "switch";
    if(state == 2)
	type = "host";
    if(state == 3)
	type = "router";
    $.post("/postAddNode",{type: type, x: xcor, y: ycor}).done( function(data){ 
	addNode(xcor, ycor, data, state);
    });
};



function saddLink(fid, sid){
    var flag = 1;
    if(fid.charAt(0) == "H")
    {
	if( !jQuery.isEmptyObject(table[fid]) )
	    flag = 0;
    }
    if(sid.charAt(0) == "H")
    {
	if( !jQuery.isEmptyObject(table[sid]) )
	    flag = 0;
    }
    if(flag == 1)
    {
	$.post("/postAddLink",{firstId: fid, secondId: sid}).done( function(data){ 
	    if(data == "success")
		addLink(fid, sid);
	});
    }
};



function sdeleteNode(id){
    $.post("/postDelNode",{id: id}).done( function(data){ 
	deleteNode(id);
    });
};



function sdeleteLink(id1, id2){
    
    $.post("/postDelLink",{firstId: id1, secondId: id2}).done( function(data){ 
	deleteLink(id1 + "_" + id2);
    });
};

