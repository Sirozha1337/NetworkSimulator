var state = 0;



function sping(firstid, secondid){
    var answer = ping(firstid,secondid);
    //display(answer);
    alert(answer);
};



function saddNode(xcor, ycor){
    $.post("/postAddNode",{type: state, x: xcor, y: ycor}).done( function(data){ 
	    alert("Hi");
	alert(data + " " + xcor + " " + ycor + "" + state);
	addNode(xcor, ycor, data, state);
    });
    aler("Bye");
};



function saddLink(fid, sid){
    var flag = 1;
    if(fid.charAt(0) == "H")
    {
	if( jQuery.isEmptyObject(table[fid]) )
	    flag = 0;
    }
    if(sid.charAt(0) == "H")
    {
	if( jQuery.isEmptyObject(table[sid]) )
	    flag = 0;
    }
    if(flag == 1)
    {
	$.post("/postAddLink",{firstid: fid, secondid: sid}).done( function(data){ 
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



function sdeleteLink(id){
    $.post("/postDelLink",{id: id}).done( function(data){ 
	deleteLink(id);
    });
};

