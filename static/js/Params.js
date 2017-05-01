function clear(){
    var configPanel = document.getElementById("configPanel");
    configPanel.innerHTML = "";
}

function save(id){
    console.log("save");

    var general = $( "#params" ).serializeArray();
    var interfaces = document.getElementsByName("interface");

    config = {};
    
    for(var i=0; i<general.length; i++){
        var name = general[i]['name'];
        var value = general[i]['value'];

        if( name ){
            config[ name ] = parseFloat(value) || value;
        }
    }

    if(interfaces.length > 0){
        config ['interfaces'] = [];
        for(var i=0; i<interfaces.length; i++){
            var intf = {};
            for(var j=0; j<interfaces[i].elements.length; j++){
                var item = interfaces[i].elements.item(j);
                intf[item.name] = item.value;            
            }
            config['interfaces'][i] = intf;
        }
    }

    console.log(JSON.stringify(config));
}

function load(id){
    clear();
    var configPanel = document.getElementById("configPanel");
    $.get("/getParams",
    {
        id: "H1"
    },
    function(data, status){
        var config = JSON.parse(data);

        // Create form
        var form = document.createElement("form");
        form.setAttribute('name', 'params');
        form.setAttribute('id', 'params');

        // Create element for name
        var l = document.createElement("label");
        l.innerHTML = "Name:";
        form.appendChild(l);
        var i = document.createElement("input");   
        i.type = "text";
        i.name = "Name";
        i.value = config['Name'];
        form.appendChild(i);

        // Create hidden elements for id and coordinates
        var i = document.createElement("input");   
        i.type = "hidden";
        i.name = "ID";
        i.value = config['ID'];
        form.appendChild(i);
        var i = document.createElement("input");   
        i.type = "hidden";
        i.name = "x";
        i.value = config['x'];
        form.appendChild(i);
        var i = document.createElement("input");   
        i.type = "hidden";
        i.name = "y";
        i.value = config['y'];
        form.appendChild(i);

        // Create elements for interfaces
        var formInterfaces = document.createElement("form");
        formInterfaces.setAttribute('id', 'interfaces');
        if('interfaces' in config){
            var l = document.createElement("label");
            l.innerHTML = "<br>Interfaces:";
            formInterfaces.appendChild(l);
            for(var intf of config['interfaces']){
                // Set interface name
                var formIntf = document.createElement("form");
                formIntf.setAttribute('name', 'interface');
                console.log(intf);
                var i = document.createElement("input");   
                i.type = "text";
                i.name = "Name";
                i.value = intf['Name'];
                formIntf.appendChild(i);
                if('IP' in intf){
                    var l = document.createElement("label");
                    l.innerHTML = "<br>IP:";
                    formIntf.appendChild(l);

                    var i = document.createElement("input");   
                    i.type = "text";
                    i.name = "IP";
                    i.value = intf['IP'];
                    formIntf.appendChild(i);
                }
                if("MAC" in intf){
                    
                    var l = document.createElement("label");
                    l.innerHTML = "<br>MAC:";
                    formIntf.appendChild(l);

                    var i = document.createElement("input");   
                    i.type = "text";
                    i.name = "MAC";
                    i.value = intf['MAC'];
                    formIntf.appendChild(i);
                }
                if("Mask" in intf){
                    
                    var l = document.createElement("label");
                    l.innerHTML = "<br>Mask:";
                    formIntf.appendChild(l);

                    var i = document.createElement("input");   
                    i.type = "text";
                    i.name = "Mask";
                    i.value = intf['Mask'];
                    formIntf.appendChild(i);
                }

                if("VLAN ID" in intf){
                    
                    var l = document.createElement("label");
                    l.innerHTML = "<br>VLAN ID:";
                    formIntf.appendChild(l);

                    var i = document.createElement("input");   
                    i.type = "text";
                    i.name = "VLAN ID";
                    i.value = intf['VLAN ID'];
                    formIntf.appendChild(i);
                }

                if("VLAN TYPE" in intf){
                    
                    var l = document.createElement("label");
                    l.innerHTML = "<br>VLAN TYPE:";
                    formIntf.appendChild(l);

                    var i = document.createElement("input");   
                    i.type = "text";
                    i.name = "VLAN TYPE";
                    i.value = intf['VLAN TYPE'];
                    formIntf.appendChild(i);
                }
                formInterfaces.appendChild(formIntf);
            }
            form.appendChild(formInterfaces); 
        }

        // Create save button
        var l = document.createElement("label");
        l.innerHTML = "<br>";
        form.appendChild(l);
        var s = document.createElement("input");
        s.type = "button";
        s.value = "Save";
        s.onclick = function handler(){ save(config['ID']); clear(); };
        form.appendChild(s);
        configPanel.appendChild(form);
    });
}

