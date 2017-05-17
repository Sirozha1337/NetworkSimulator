/* Data structure for storing links */
var table = new Object();

/* Currently chosen device for pinging */
var pingId = "";

/* Device to remove id */
var delId = "";

/* Currently chosen device to connect line to */
var linkId = "";

/* Function which finds objects on canvas by their myName value */
fabric.Canvas.prototype.getItemByName = function(name) {
    var object = null,
    objects = this.getObjects();
    for (var i = 0, len = this.size(); i < len; i++) {
        if (objects[i].myName && objects[i].myName === name) {
	        object = objects[i];
	        break;
	    }
    }					     
    return object;
};

/* Function which removes link between two nodes and removes it from the link table */
function deleteLink(id){
    var tmpline = canvas.getItemByName(id);
    var names = tmpline.myName.split("_");
    delete table[names[0]][names[1]];
    delete table[names[1]][names[0]];
    tmpline.remove();
};

function lineLength(node1, node2){
    return node1.left + Math.pow(Math.pow(node2.width/2 , 2) + Math.pow(node2.height/2 ,2), 1/2) 
                 + Math.pow(Math.pow(node2.left - node1.left , 2) + Math.pow(node2.top - node1.top ,2), 1/2);
};

function lineAngle(node1, node2){
    return Math.atan((node2.top - node1.top)/(node2.left - node1.left)) * (180/Math.PI);
};

/* Creates link between two nodes and add it to the link table */
function addLink(firstId, secondId){
    var rect1 = canvas.getItemByName(firstId);
    var rect2 = canvas.getItemByName(secondId);
    
    if(rect1.left > rect2.left){
        rect2 = rect1;
        rect1 = canvas.getItemByName(secondId);
    }
    var length = lineLength(rect1, rect2);
    var line = new fabric.Line([rect1.left+rect1.width/2, rect1.top+rect1.height/2, length , rect1.top+rect1.height/2], {
        strokeWidth: 5,
        fill: 'black',
        stroke: 'black',
        angle: lineAngle(rect1, rect2),
        myName: firstId + "_" + secondId,
        lockMovementX: true,
        lockMovementY: true,
        hasControls: false,
        hasBorders: false,
        hoverCursor: 'pointer'
    });

    canvas.add(line);      
    canvas.sendToBack(line)
    
    line.on('mousedown', function(e){
	    if(delId !== line.myName){
	        delId = line.myName;
	    }
	    else{
            sdeleteLink(firstId, secondId);
	    }
	    pingId = "";
	    linkId = "";
    });
    
    table[firstId][secondId] = table[secondId][firstId] = line;
    turnOffSelection(secondId);
};

/* Remove node from canvas */
function deleteNode(id){
    for(name in table[id]){
        var tmpline = table[id][name];
        tmpline.remove();
    }				       
    delete table[id];
    for(name in table){
        if(table[name].hasOwnProperty(id)){
            delete table[name][id];
        }
    }
    canvas.remove(canvas.getItemByName(id));
};

/* Ping second host from first */
function ping(first, second){
    $.get("/getPing",{sender: first, receiver: second}).done( function(data){
        turnOffSelection(second);
        turnOffSelection(first);
	    var mes = first + " ping " + second + "\n" + data;
	    display(mes);
    });
};

/* Add node to the canvas */
function addNode(corx, cory, id, type){
    var hostImage = document.getElementById("host");
    var switchImage = document.getElementById("switch");
    var routerImage = document.getElementById("router");
    var gearImage = document.getElementById('gear');
    var crossImage = document.getElementById('cross');

    var selectedHostImage = document.getElementById("shost");
    var selectedSwitchImage = document.getElementById("sswitch");
    var selectedRouterImage = document.getElementById("srouter");

    var node;
    var regular;
    var selected;
    var mousedown;
    switch(type){
        case "Switches":  regular = switchImage;
                        selected = selectedSwitchImage;
                        mousedown = function(e){
		                    if(pingId != ""){
		                        turnOffSelection(pingId);
		                    }
		                    else if(linkId != ""){
		                        turnOffSelection(linkId);
		                    }
		
		                    pingId = "";
		                    if(state == "link"){
                                node.setElement(selected, function(){}, {width: 100, height: 40});
		                        if(linkId == "" || linkId == id){
			                        linkId = id;
                                }
		                        else{
			                        saddLink(linkId, id);
                                    linkId = "";
                                }
		                    }
                        };
                        break;

        case "Hosts":   regular = hostImage;
                        selected = selectedHostImage;
                        mousedown = function(e){
                            node.setElement(selected, function(){}, {width: 100, height: 40});
	                        
                            if(linkId != ""){
		                        turnOffSelection(linkId);
                            }
	                        
		                    if(state == "link"){
			                    pingId = "";
			                    if(linkId == "" || linkId == id)
			                        linkId = id;
			                    else{
			                        saddLink(linkId, id);
                                    linkId = "";
                                }
		                    }
                            else{
		                        linkId = "";
		                        if(state == "ping"){
		                            if(pingId == ""){
			                            pingId = id;
		                            }
		                            else{
			                            if(pingId != id){
			                                var tmp = pingId;
			                                pingId = "";
		                                    sping(tmp, id);
			                            }
		                            }
		                        }
                            }
                        };  
                        break;
                    
            case "Routers":    
                        regular = routerImage;
                        selected = selectedRouterImage;
                        mousedown = function(e){
		                    if(pingId != ""){
		                        turnOffSelection(pingId);
		                    }
		                    else if(linkId != ""){
		                        turnOffSelection(linkId);
		                    }
		
		                    pingId = "";
		                    if(state == "link"){
                                node.setElement(selected, function(){}, {width: 100, height: 40});
		                        if(linkId == "" || linkId == id){
			                        linkId = id;
                                }
		                        else{
			                        saddLink(linkId, id);
                                    linkId = "";
                                }
		                    }
                        };
                        break;        
    }
    node = new fabric.Image(regular, {width:100, height:40,top:20}); 
    node.myName = id + "_Icon";
    node.on('mouseup', function(e){
        canvas.discardActiveObject();
        canvas.renderAll(); 
    });
    node.on('mousedown', mousedown);

    var gear = new fabric.Image(gearImage, {width:20, height:20, left:100, top:20});
    gear.myName= id + "_Gear";
    gear.on('mousedown', function(e){
            canvas.discardActiveObject();
            canvas.renderAll(); 
	        load(id);
    });
    
    var cross = new fabric.Image(crossImage, {width:20, height:20, left:100, top: 40});
	cross.myName= id + "_Cross";
	cross.on('mousedown', function(e){
        canvas.discardActiveObject();
        canvas.renderAll(); 
	    pingId = "";
	    linkId = "";
		sdeleteNode(id);
	});
		    
	var mytext = new fabric.Text(id, {left: 0, myName: id + "_Text"});
	    
	mytext.scaleToHeight(20);
	var mygroup =   new fabric.Group([ node, gear, cross, mytext], { left: corx, top: cory, myName: id, 
                                                                    subTargetCheck: true, hasControls: false, 
                                                                    hasBorders: false, hoverCursor:'pointer', 
                                                                    objectCaching: false});
		    
	mygroup.on('moving', function(e){
		for(name in table[id]){
		    var tmpline = table[id][name];
		    var tmpr1 = mygroup;
		    var tmpr2 = canvas.getItemByName(name);
		    if(tmpr1.left > tmpr2.left){
                tmp = tmpr2;
			    tmpr2 = tmpr1;
			    tmpr1 = tmp;
		    }
		    var length = lineLength(tmpr1, tmpr2); 

		    var newangle = lineAngle(tmpr1, tmpr2);
		    tmpline.set({x1: tmpr1.left+tmpr1.width/2, x2: length, 
                         y1: tmpr1.top+tmpr1.height/2, y2: tmpr1.top+tmpr1.height/2,
                         angle: newangle});  
		    tmpline.setCoords();  
		    pingId = ""; 
		    linkId = "";
		    
            node.setElement(regular, function(){}, {width: 100, height: 40});

		    canvas.renderAll(); 
		}
	});
	    
	mygroup.on('mousedown', function(e){
		delId = "";
	});

    canvas.add(mygroup); 
	canvas.renderAll(); 
	table[id] = new Object();	
};

/* Load topology from json file */
function loadTopology(){
    $.get("/getSavedTopo",function(canvasTable){ 
        var nodeTypes = ["Hosts", "Switches", "Routers"];
        for(var i = 0; i < nodeTypes.length; i++){
	        if( canvasTable.hasOwnProperty(nodeTypes[i]) ){
                for(index in canvasTable[nodeTypes[i]]){
		            var id = canvasTable[nodeTypes[i]][index]["ID"];
		            var x = canvasTable[nodeTypes[i]][index]["x"];
		            var y = canvasTable[nodeTypes[i]][index]["y"];
		            addNode( x, y, id, nodeTypes[i] );
		            changeName(id,canvasTable[nodeTypes[i]][index]["Name"]);
	            }
	        }
        }
	    if( canvasTable.hasOwnProperty("Links") ){
	        for(index in canvasTable["Links"]){
		        var id1 = canvasTable["Links"][index][0];
		        var id2 = canvasTable["Links"][index][1];
		        addLink(id1, id2);
	        }
	    }
    });
};

/* Change display name */
function changeName(id,name){
    var tmp = canvas.getItemByName(id);
    tmp.item(3).setText(name);
    canvas.renderAll();
};

/* Turn off object selection */
function turnOffSelection(id){
    var tmp = canvas.getItemByName(id);
    var src = "";
    if(id.charAt(0) == "S")
        src = document.getElementById("switch");
    else
        if(id.charAt(0) == "H")
            src = document.getElementById("host");
        else
            src = document.getElementById("router");
    tmp.item(0).setElement(src, function(){}, {width: 100, height: 40});
    canvas.renderAll(); 
};
