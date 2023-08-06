// s4 javascript utils (drive utils)
// author: Ondrej Sika, http://ondrejsika.com

function s4Upload(uri, file, callback, error, async) {
    if (async === undefined) async = true;
    xhr = new XMLHttpRequest();
    fd = new FormData();
    xhr.open("POST", uri, async);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            callback(xhr.responseText);
        }
        if (xhr.readyState == 4 && xhr.status != 200) {
            error(xhr.status, xhr.responseText, xhr)
        }
    }
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
