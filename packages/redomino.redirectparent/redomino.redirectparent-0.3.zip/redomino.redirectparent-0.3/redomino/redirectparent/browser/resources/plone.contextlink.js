(function (w){

$(document).ready(function (){
    if(w.REDIRECT_TO_PARENT){
        $('.relatesToUID').contextlink('relatesToUID', w.REDIRECT_TO_PARENT.obj_uid || 'None');
    }
//    $('.relatesToPath').contextlink('relatesToPath', REDIRECT_TO_PARENT.obj_path);
//    $('.relatesToURL').contextlink('relatesToURL');
});

}(window));
