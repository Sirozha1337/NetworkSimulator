var state = "link";

function changeState(newState){
    if(state === newState)
        state = "link";
    else{
        state = newState;
    }
    switch(state){
        case "link": { 
            $( "#hostButton" ).removeClass('active'); 
            $( "#switchButton" ).removeClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            break;
        }
        case "switch":{ 
            $( "#hostButton" ).removeClass('active'); 
            $( "#switchButton" ).addClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            break;
        }
        case "host":{ 
            $( "#hostButton" ).addClass('active'); 
            $( "#switchButton" ).removeClass('active'); 
            $( "#pingButton" ).removeClass('active'); 
            break;
        }
        case "ping":{ 
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
    var tmp = state;
    console.log(tmp);
    $.post("/postAddNode",{type: tmp, x: xcor, y: ycor}).done( 
        function(data){ 
	        addNode(xcor, ycor, data, tmp);
        }
    );
};



function saddLink(fid, sid){
    turnOffSelection(sid);
    var flag = 1;
    if(fid.charAt(0) == "H"){
	    if( !jQuery.isEmptyObject(table[fid]) )
	        flag = 0;
    }
    if(sid.charAt(0) == "H"){
	    if( !jQuery.isEmptyObject(table[sid]) )
	        flag = 0;
    }
    if(flag == 1){
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

