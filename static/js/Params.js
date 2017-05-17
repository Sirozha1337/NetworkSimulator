function clear(){
    //var configPanel = document.getElementById("configPanel");
    configPanel.innerHTML = "";
}

function save(id){

    var general = $( "#params" ).serializeArray();
    var interfaces = document.getElementsByName("interface");

    config = {};
    for(var i=0; i<general.length; i++){
        var name = general[i]['name'];
        var value = general[i]['value'];

        if( name != 'State' ){
            config[ name ] = parseFloat(value) || value;
        }
        else{
            config[ name ] = true;
        }
    }
    if(config['State'] == null)
        config['State'] = false;
    changeName(config['ID'], config['Name']);

    var object = canvas.getItemByName(config['ID'])

    config['x'] = object.oCoords['tl'].x;
    config['y'] = object.oCoords['tl'].y;   

    if(interfaces.length > 0){
        config ['interfaces'] = [];
        for(var i=0; i<interfaces.length; i++){
            var intf = {};
            for(var j=0; j<interfaces[i].elements.length; j++){
                var item = interfaces[i].elements.item(j);
                intf[item.name] = item.value; 
                if(item.name === 'VLAN ID')
                    intf[item.name] = parseInt(item.value)          
            }
            config['interfaces'][i] = intf;
        }
    }

    
    $.post("/postParams",{id: id, config: JSON.stringify(config)}).done( function(data){ 
    });
}

// Disable submit on enter for forms
window.addEventListener('keydown', function(e) {
    if (e.keyIdentifier == 'U+000A' || e.keyIdentifier == 'Enter' || e.keyCode == 13) {
        if (e.target.nodeName == 'INPUT' && e.target.type == 'text') {
            e.preventDefault();
            return false;
        }
    }
}, true);

/* Create label with specified text and append it to specified parent */
function createLabel(text, parent){
    var l = document.createElement("label");
    l.innerHTML = text;
    parent.appendChild(l);
};

function createInputField(type, name, value, pattern, parent, required, disabled){
    var i = document.createElement("input");   
    i.type = type;
    i.name = name;
    i.value = value;
    if(pattern != "")
        i.pattern = pattern;
    i.required = required;
    i.disabled = disabled;
    parent.appendChild(i);
}; 

function load(id){
    clear();
    var configPanel = document.getElementById("configPanel");
    $.get("/getParams",
    {
        id: id
    },
    function(data, status){
        var config = JSON.parse(data);
        // Create form
        var form = document.createElement("form");
        form.setAttribute('name', 'params');
        form.setAttribute('id', 'params');
        // Create element for name
        createLabel("Name:", form);
        createInputField("text", "Name", config['Name'], "[A-Za-zА-Яа-яЁё0-9 ]+", form, true, false);

        // Create hidden elements for id and coordinates
        if('DPID' in config){
            createInputField("hidden", "DPID", config['DPID'], "", form);
        }

        createInputField("hidden", "ID", config['ID'], "", form);    
        createInputField("hidden", "x", config['x'], "", form);    
        createInputField("hidden", "y", config['y'], "", form);   

        // Create elements for interfaces
        var formInterfaces = document.createElement("div");
        formInterfaces.setAttribute('id', 'interfaces');
        formInterfaces.setAttribute('style', 'overflow-y: scroll; height: 250px;');
        if('interfaces' in config){
            createLabel("<br>Interfaces:", formInterfaces);

            for(var intf of config['interfaces']){
                // Set interface name
                var formIntf = document.createElement("form");
                formIntf.setAttribute('name', 'interface');
                formIntf.setAttribute('id', 'params');

                createInputField("text", "Name", intf['Name'], "", formIntf, false, true);   
                if('IP' in intf){
                    createLabel("<br>IP:", formIntf);
                    createInputField("text", "IP", intf['IP'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formIntf, true, false);   
                }
                if("Mask" in intf){
                    createLabel("<br>Mask:", formIntf);
                    createInputField("text", "Mask", intf['Mask'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formIntf, true, false);  
                }
                if("MAC" in intf){
                    createLabel("<br>MAC:", formIntf);
                    createInputField("text", "MAC", intf['MAC'], "[0-9a-f][0-9a-f]:[0-9a-f][0-9Aa-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]", formIntf, true, false); 
                }

                if("VLAN ID" in intf){
                    createLabel("<br>VLAN ID:", formIntf);
                    createInputField("text", "VLAN ID", intf['VLAN ID'], "([0-4]?[0-9]?[0-9])|(50[1-9])|(51[0-2])", formIntf, true, false);  
                }

                if("VLAN TYPE" in intf){
                    createLabel("<br>VLAN TYPE:", formIntf);

                    var i = document.createElement("select");
                    i.name = "VLAN TYPE";
                    var option1 = document.createElement("option");
                    option1.value = "access";
                    option1.text = "access";
                    var option2 = document.createElement("option");
                    option2.value = "dot1q";
                    option2.text = "dot1q";
                    if(intf['VLAN TYPE'] == "access")
                        option1.selected = true;
                    else
                        option2.selected = true;
                    i.appendChild(option1);
                    i.appendChild(option2);
                    formIntf.appendChild(i);
                }
                formInterfaces.appendChild(formIntf);
            }
            form.appendChild(formInterfaces); 
        }
        // Create state
        if('State' in config){
            var l = document.createElement("label");
            l.setAttribute('class', 'switch');
            var i = document.createElement("input");
            i.setAttribute('type', 'checkbox');
            i.checked = config['State'];
            i.name = 'State';
            var d = document.createElement("div");
            d.setAttribute('class', 'slider round');
            l.appendChild(i);
            l.appendChild(d);
            form.appendChild(l);
        }
        // Create save button
        createLabel("<br>", form);
        var s = document.createElement("input");
        s.type = "submit";
        s.value = "Save";
        s.onclick = function handler(e){ 
            e.preventDefault();
            var fields = document.getElementsByTagName('input');
            var valid = true;
            for(var i=0; i < fields.length; i++)
            { 
                valid = valid && fields[i].checkValidity();
            }
            if(valid){
                save(config['ID']); 
                /*clear();*/
            } 
        };
        configPanel.appendChild(form);
        configPanel.appendChild(s);
    });
}

