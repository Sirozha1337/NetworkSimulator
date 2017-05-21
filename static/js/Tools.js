var state = "link";

function changeState(newState){
    if(state === newState)
        state = "link";
    else{
        state = newState;
    }
    
    $( "#hostButton" ).removeClass('active'); 
    $( "#switchButton" ).removeClass('active'); 
    $( "#routerButton" ).removeClass('active'); 
    $( "#pingButton" ).removeClass('active'); 
    switch(state){
        case "link": break;
        case "Switches": $( "#switchButton" ).addClass('active'); break;
        case "Hosts": $( "#hostButton" ).addClass('active'); break;
        case "Routers": $( "#routerButton" ).addClass('active'); break;
        case "ping": $( "#pingButton" ).addClass('active'); break;
    }
};



function sping(firstid, secondid){
    ping(firstid,secondid);
};



function saddNode(xcor, ycor){
    var tmp = state;
    $.post("/postAddNode",{type: tmp, x: xcor, y: ycor}).done( 
        function(data){ 
	        addNode(xcor, ycor, data, tmp);
        }
    );
};



function saddLink(fid, sid){
    $.post("/postAddLink",{firstId: fid, secondId: sid}).done( function(data){ 
        if(data == "success")
	        addLink(fid, sid);
    });
};



function sdeleteNode(id){
    $.post("/postDelNode",{id: id}).done( function(data){ 
	    deleteNode(id);
    });
};



function sdeleteLink(id1, id2){
    
    $.post("/postDelLink",{firstId: id1, secondId: id2}).done( function(data){ 
	    deleteLink(id1, id2);
    });
};

