var table = new Object();
var pingId = "";
var delId = "";

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

function deleteLink(id){
    var tmpline = canvas.getItemByName(id);
    var names = tmpline.myName.split("_");
    delete table[names[0]][names[1]];
    delete table[names[1]][names[0]];
    tmpline.remove();
};

function addLink(firstId, secondId){
    var rect1 = canvas.getItemByName(firstId);
    var rect2 = canvas.getItemByName(secondId);
    
    if(rect1.left > rect2.left){
        rect2 = rect1;
        rect1 = canvas.getItemByName(secondId);
    }
    var length = rect1.left + Math.pow(Math.pow(rect2.width/2 , 2) + Math.pow(rect2.height/2 ,2), 1/2) + Math.pow(Math.pow(rect2.left - rect1.left , 2) + Math.pow(rect2.top - rect1.top ,2), 1/2);      
    var line = new fabric.Line([rect1.left+rect1.width/2, rect1.top+rect1.height/2, length , rect1.top+rect1.height/2], {
        strokeWidth: 5,
        fill: 'black',
        stroke: 'black',
        angle: Math.atan((rect2.top - rect1.top)/(rect2.left - rect1.left)) * (180/Math.PI),
        myName: firstId + "_" + secondId
        
    });
    canvas.add(line);      
    canvas.sendToBack(line)
    line.lockMovementX = line.lockMovementY = true;
    line.hasControls = line.hasBorders = false;
    line.hoverCursor = 'pointer';
    
    line.on('mousedown', function(e){
	if(delId !== line.myName){
	    delId = line.myName;
	}
	else{
            deleteLink(line.myName);
	}
	pingId = "";
    });
    
    table[firstId][secondId] = table[secondId][firstId] = firstId + "_" + secondId; 
};

function deleteNode(id){
    for(name in table[id]){
        var tmpline = canvas.getItemByName(table[id][name]);
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

function ping(fpid, spid){
    $.get("/getPing",{sender: fpid, reciver: spid}).done( function(data){ 
	return data; 
    });
};

function addNode(corx, cory, id, type){
    var hostImage = document.getElementById("host");
    var switchImage = document.getElementById("switch");
    var routerImage = document.getElementById("router");
    var gearImage = document.getElementById('gear');
    var crossImage = document.getElementById('cross');
    if(type === 1){
        var sw = new fabric.Image(switchImage, {width:160, height:60,top:20});
        sw.myName= id + "_Icon";
	    sw.on('mousedown', function(e){
		    pingId = "";
        });
	    var gear = new fabric.Image(gearImage, {width:20,height:20,left:140});
		gear.myName= id + "_Gear";
		
		var cross = new fabric.Image(crossImage, {width:20,height:20,left:120});
		cross.myName= id + "_Cross";
		cross.on('mousedown', function(e){
			deleteNode(id);
		});
		    
		var mytext = new fabric.Text(id, {left: 0, myName: id + "_Text"});
		    
		mytext.scaleToHeight(20);
		var mygroup =   new fabric.Group([ sw, gear, cross, mytext], { left: corx, top: cory, myName: id, subTargetCheck: true, hasControls: false, hasBorders: false});
		    
		mygroup.on('moving', function(e){
			for(name in table[id]){
			    var tmpline = canvas.getItemByName(table[id][name]);
			    var names = tmpline.myName.split("_");
			    var tmpr1 = canvas.getItemByName(names[0]);
			    var tmpr2 = canvas.getItemByName(names[1]);
			    if(tmpr1.left > tmpr2.left){
				    tmpr2 = tmpr1;
				    tmpr1 = canvas.getItemByName(names[1]);
			    }
			    var length = tmpr1.left + Math.pow(Math.pow(tmpr2.width/2 ,2) 
                                        + Math.pow(tmpr2.height/2 ,2), 1/2) 
                                        + Math.pow(Math.pow(tmpr2.left - tmpr1.left,2) 
                                        + Math.pow(tmpr2.top - tmpr1.top,2), 1/2);
			    var newangle = Math.atan((tmpr2.top - tmpr1.top)/(tmpr2.left - tmpr1.left)) * (180/Math.PI);
			    tmpline.set({x1: tmpr1.left+tmpr1.width/2, x2: length, 
                             y1: tmpr1.top+tmpr1.height/2, y2: tmpr1.top+tmpr1.height/2,
                             angle: newangle});  
			    tmpline.setCoords();  
			    canvas.renderAll(); 
			    pingId = "";          
			}
		});
		    
		mygroup.on('mousedown', function(e){
			delId = "";
		});
		    
	    canvas.add(mygroup);
		table[id] = new Object();	
    }
    
    if(type === 2){
        var host = new fabric.Image(hostImage, {width:160, height:60,top:20});
        console.log(hostImage);
        host.myName = id + "_Icon";
        host.on('mousedown', function(e){
		    if(pingId == ""){
		        pingId = id;
		    }
		    else{
		        if(pingId != id){
			        ping(pingId, id);
			        pingId = "";
		        }
		    }
        });
        var gear = new fabric.Image(gearImage, {width:20,height:20,left:140});
        gear.myName = id + "_Gear";
        
        var cross = new fabric.Image(crossImage, {width:20,height:20,left:120});
        cross.on('mousedown', function(e){
			    deleteNode(id);
		});

        var mytext = new fabric.Text(id, {left: 0, myName: id + "_Text"});

        mytext.scaleToHeight(20);

        var mygroup = new fabric.Group([ host, gear, cross, mytext], { left: corx, top: cory, myName: id, subTargetCheck: true, hasControls: false, hasBorders: false});
        
        mygroup.on('moving', function(e){
			for(name in table[id]){
			    var tmpline = canvas.getItemByName(table[id][name]);
			    var names = tmpline.myName.split("_");
			    var tmpr1 = canvas.getItemByName(names[0]);
			    var tmpr2 = canvas.getItemByName(names[1]);
			    if(tmpr1.left > tmpr2.left){
				    tmpr2 = tmpr1;
				    tmpr1 = canvas.getItemByName(names[1]);
			    }
			    var length = tmpr1.left + Math.pow(Math.pow(tmpr2.width/2 ,2) 
                                        + Math.pow(tmpr2.height/2 ,2), 1/2) 
                                        + Math.pow(Math.pow(tmpr2.left - tmpr1.left,2) 
                                        + Math.pow(tmpr2.top - tmpr1.top,2), 1/2);
			    var newangle = Math.atan((tmpr2.top - tmpr1.top)/(tmpr2.left - tmpr1.left)) * (180/Math.PI);
			    tmpline.set({x1: tmpr1.left+tmpr1.width/2, x2: length, y1: tmpr1.top+tmpr1.height/2, y2: tmpr1.top+tmpr1.height/2, angle: newangle}); 
			    tmpline.setCoords(); 
			    canvas.renderAll();
			    pingId = "";   
			}
		});

        mygroup.on('mousedown', function(e){
			delId = "";
		});

        canvas.add(mygroup);
		table[id] = new Object();	
        console.log('object added to canvas');
    }
    
    if(type === 3){
        fabric.Image.fromURL('./static/img/router.jpg', function(oImg) {      
            var img1 = oImg.set({width:160, height:60,top:20});
            img1.myName= id + "_Icon";
	    
            img1.on('mousedown', function(e){
		if(pingId == ""){
		    pingId = id;
		}
		else{
		    if(pingId != id)
		    {
			ping(pingId, id);
			pingId = "";
		    }
		}
            });
	    
            fabric.Image.fromURL('./static/img/gear.png', function(oImg) {
		var img2 = oImg.set({width:20,height:20,left:140});
		img2.myName= id + "_Gear";
		
		fabric.Image.fromURL('./static/img/cross.png', function(oImg) {
		    var img3 = oImg.set({width:20,height:20,left:120});
		    img3.myName= id + "_Cross";
		    
		    img3.on('mousedown', function(e){
			deleteNode(id);
		    });
		    
		    var mytext = new fabric.Text(id, {left: 0, myName: id + "_Text"});
		    mytext.scaleToHeight(20);
		    var mygroup =   new fabric.Group([ img1, img2, img3, mytext], { left: corx, top: cory, myName: id, subTargetCheck: true, hasControls: false, hasBorders: false});
		    
		    mygroup.on('moving', function(e){
			for(name in table[id]){
			    var tmpline = canvas.getItemByName(table[id][name]);
			    var names = tmpline.myName.split("_");
			    var tmpr1 = canvas.getItemByName(names[0]);
			    var tmpr2 = canvas.getItemByName(names[1]);
			    if(tmpr1.left > tmpr2.left){
				tmpr2 = tmpr1;
				tmpr1 = canvas.getItemByName(names[1]);
			    }
			    var length = tmpr1.left + Math.pow(Math.pow(tmpr2.width/2 ,2) + Math.pow(tmpr2.height/2 ,2), 1/2) + Math.pow(Math.pow(tmpr2.left - tmpr1.left,2) + Math.pow(tmpr2.top - tmpr1.top,2), 1/2);
			    var newangle = Math.atan((tmpr2.top - tmpr1.top)/(tmpr2.left - tmpr1.left)) * (180/Math.PI);
			    tmpline.set({x1: tmpr1.left+tmpr1.width/2, x2: length, y1: tmpr1.top+tmpr1.height/2, y2: tmpr1.top+tmpr1.height/2, angle: newangle}); 
			    tmpline.setCoords();  
			    canvas.renderAll();   
			    pingId = "";             
			}
		    });
		    
		    mygroup.on('mousedown', function(e){
			delId = "";
		    });
		    
		    canvas.add(mygroup);
		    table[id] = new Object();			       
		});
            });
        });		
    }
};

function loadTopology(){

    $.get("/getSavedTopo",function(canvasTable){ 	
	if( canvasTable.hasOwnProperty("Hosts") ){
        for(index in canvasTable["Hosts"]){
		    var id = canvasTable["Hosts"][index]["ID"];
		    var x = canvasTable["Hosts"][index]["x"];
		    var y = canvasTable["Hosts"][index]["y"];
		    addNode(x,y,id,2);
		    changeName(id,canvasTable["Hosts"][index]["Name"]);
	    }
	}
	if( canvasTable.hasOwnProperty("Switches") ){
	    for(index in canvasTable["Switches"]){
		    var id = canvasTable["Switches"][index]["ID"];
		    var x = canvasTable["Switches"][index]["x"];
		    var y = canvasTable["Switches"][index]["y"];
		    addNode(x,y,id,1);
		    changeName(id,canvasTable["Switches"][index]["Name"]);
	    }
	}
	if( canvasTable.hasOwnProperty("Routers") ){
	    for(index in canvasTable["Routers"]){
		    var id = canvasTable["Routers"][index]["id"];
		    var x = canvasTable["Routers"][index]["x"];
		    var y = canvasTable["Routers"][index]["y"];
		    addNode(x,y,id,3);
		    changeName(id,canvasTable["Routers"][index]["Name"]);
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

function changeName(id,name){
    var tmp = canvas.getItemByName(id);
    tmp.item(3).setText(name);
    canvas.renderAll();
};
