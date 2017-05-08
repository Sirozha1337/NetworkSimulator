var state = 0;



function changeState(newState){
    if(state == newState)
        state = 0;
    else{
        state = newState;
    }
    switch(state){
        case 0: { 
            $( "#hostButton" ).removeClass('active'); 
            $( "#switchButton" ).removeClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            break;
        }
        case 1:{ 
            $( "#hostButton" ).removeClass('active'); 
            $( "#switchButton" ).addClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            console.log($( "#switchButton" ));
            break;
        }
        case 2:{ 
            $( "#hostButton" ).addClass('active'); 
            $( "#switchButton" ).removeClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            break;
        }
        case 4:{ 
            $( "#hostButton" ).removeClass('active'); 
            $( "#switchButton" ).removeClass('active'); 
            $( "#pingButton" ).addClass('active'); 
            break;
        }
    }
};



function sping(firstid, secondid){
    ping(firstid,secondid);
};



function saddNode(xcor, ycor){
    var type;
    var tmp = state;
    if(state == 1)
	    type = "switch";
    if(state == 2)
	    type = "host";
    if(state == 3)
	    type = "router";
    $.post("/postAddNode",{type: type, x: xcor, y: ycor}).done( 
        function(data){ 
            console.log("addnode1");
	        addNode(xcor, ycor, data, tmp);
            console.log("addnode2");
        }
    );
};



function saddLink(fid, sid){
    turnOffSelection(sid);
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

