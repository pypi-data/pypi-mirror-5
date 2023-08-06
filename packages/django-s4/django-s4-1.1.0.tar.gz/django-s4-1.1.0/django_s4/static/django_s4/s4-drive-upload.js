// s4 javascript utils (drive utils)
// author: Ondrej Sika, http://ondrejsika.com

function s4Upload(uri, file, callback) {
   var xhr = new XMLHttpRequest();
   var fd = new FormData();
   xhr.open("POST", uri, true);
   xhr.onreadystatechange = function() {if (xhr.readyState == 4 && xhr.status == 200) {callback(xhr.responseText);}};
   fd.append('file', file);
   xhr.send(fd);
}

function s4MultiUpload(uri, files, callback, loopInterval) {
    if (loopInterval == undefined) loopInterval = 300;
    var responses = []; 
    for (var i = 0; i < files.length; i++) {
        s4Upload(uri, files[i], function(data){
            responses.push(data);
        }); 
    };  
    var loop = setInterval(function(){
        if (responses.length == files.length) {
            clearInterval(loop);
            callback(responses);
        }   
    }, loopInterval);
}
