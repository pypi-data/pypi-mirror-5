$(function(){$("#tabs").tabs();});
 
function showHide(cb,num)
{
    // show or hide a form depending on status of checkbox
    if(cb.checked == true){
        document.getElementById("data"+num).style.display="inline";
    }else{
        document.getElementById("data"+num).style.display="none";
    }
    showHideSubmit();
}

function showHideSubmit()
{
    // show or hide submission button depending on if any checkboxes are checked for machines
    //  that are eligible to be submitted
    var checkboxes = document.getElementsByClassName("check");
    var checked = 0;
    for(var i = 0; i < checkboxes.length; i++){
        if(checkboxes[i].checked == true && checkboxes[i].disabled == false){
            checked = 1;
        }
    }
    if(checked == 1){
        document.getElementById("submit_button").style.display="block";
    }else{
        document.getElementById("submit_button").style.display="none";
    }
}

function submitForms()
{
    //submit each form that has a checked checkbox and has not been submitted yet
    var checkboxes = document.getElementsByClassName("check");
    
    // make sure no input information is missing
    var missing = 0;
    for(var i = 0; i < checkboxes.length; i++){
        if(checkboxes[i].checked == true && checkboxes[i].disabled == false){
            var num = checkboxes[i].name.match(/\d+$/)[0];
            for(var x = 0; x < window.inputs.length; x++){
                if(document.getElementsByName(window.inputs[x]+num)[0].value == ""){
                     document.getElementById(window.inputs[x]+num+"req").style.display="block";
                     missing = 1;
                }else{
                    document.getElementById(window.inputs[x]+num+"req").style.display="none";
                }
            }
        }
    }

    if(missing == 1){
        alert("Please fill out all fields");
        return false;
    }

    // make sure that there is no repeated data
    for(var i = 0; i<checkboxes.length; i++){
        if(checkboxes[i].checked == true){
            var numi = checkboxes[i].name.match(/\d+$/)[0];
            for(var x = i+1;x<checkboxes.length;x++){
                if(checkboxes[x].checked == true){
                    var numx = checkboxes[x].name.match(/\d+$/)[0];
                    if($("#hostname"+numi).val() == $("#hostname"+numx).val()){
                        alert('Hostnames must be unique');
                        return false;
                    }
                }
            }
        }
    }
    var r = confirm("Did you forget something? Please make sure that all information is correct.");
    if(r == true){
        // finally submit each eligible form
        for(var i = 0; i < checkboxes.length; i++){
            if(checkboxes[i].checked == true && checkboxes[i].disabled == false){
                //derive form name and submit to be input into db
                var num = checkboxes[i].name.match(/\d+$/)[0];
                var form_name = "form".concat(num);
                var form = document.getElementsByName(form_name)[0];
                var serializedData = $("#form"+num).serialize();
                // in addition to updating info add this to job tracker
                $.ajax({
                    url: "sent/"+num+"/",
                    type: "post",
                    data: serializedData,
                    cache: 'false',
                    dataType: "json",
                    async: 'false',

                    success: function(data){successful_post(data);},
                    error: function(jqXHR, textStatus, errorThrown) {alert(textStatus);alert(errorThrown);}
                });
            }
        }
    } else {
        return false;
    }
}

function successful_post(data){
    // deactivate all input in the form
    deactivateForm(data.num);
    // start periodic status check/update
    initstartCheck(data);
}
// need to change the status check to check every in progress job instead of just one
// think about having one interval that is connected to window
// window.data-mach_info-interval-id=intervalId;
//  this interval should only be started once i.e. when the first job is started
//  and should only stop when the last job is done/there are no more jobs in progress
// should return all of the statuses then update 
function initstartCheck(data){
    document.getElementById('status'+data.num).style.display = 'inline';
    $('#status'+data.num).html("Step "+data.status+" of "+data.done+" : "+data.message);
    demo(data.num);
    initInterval();
}
 
function startCheck(){
    cumulative_stat_check();
    initInterval();
}
function demo(num){
    if(num != 0){
        $.ajax({
            url: "demo_status/"+$("#svctag"+num).val()+"/",
            type: "get",
            cache: 'false',
            dataType: "json",
            async: 'true',
            
            success: function(data){},
            error: function(jqXHR, textStatus, errorThrown) {alert(textStatus);alert(errorThrown);}
        });
    }
}

function initInterval(){
    // check if interval was already started/still running
    // use window.checkstarted = "true" or "false"
    if(window.checkstarted == "false"){
        var intervalId = setInterval(function(){cumulative_stat_check()},30000);
        window.checkstarted = "true";
        // add data attribute for intervalId to the window so it can be accessed later
        window.intervalid = intervalId;
    }
}

function deactivateForm(num){
    for(var i = 0;i < window.inputs.length; i++){
        document.getElementsByName(window.inputs[i]+num)[0].disabled = true;
    }
    document.getElementsByName("svctag"+num)[0].disabled = true;
    showHideSubmit();
}

function cumulative_stat_check(){
    // check status of all running jobs
    $.ajax({
        url: "allstatus/",
        type: "get",
        cache: 'false',
        dataType: 'json',
        async: 'true',
        success: function(data) {
            var completed = 1;
            var checkboxes = document.getElementsByClassName("check");
            // run through each job that is in progress and update status accordingly
            for(var i=0;i<data.jobs.length;i++){
                for(var j=0;j<checkboxes.length;j++){
                    if(checkboxes[j].value == data.jobs[i].name){
                        var num = checkboxes[j].name.match(/\d+$/)[0];
                    }
                }
                // display the status of the job
                if(document.getElementById('status'+num).style.display == 'none'){
                    document.getElementById('status'+num).style.display = 'inline';
                }
                $('#status'+num).html("Step "+data.jobs[i].status+" of "+data.done+" : "+data.jobs[i].message);
                if(data.jobs[i].status != data.done){
                    completed = 0;
                }else{
                    // display the delete image and hide the checkbox so that when they want to the user can remove the job from being displayed
                    document.getElementById('svctag'+num).style.display = 'none';
                    document.getElementById('delete'+num).style.display = 'inline';
                }
            }
            // stop checking the status when all jobs are complete
            // keep checking even if only one is still active
            if(completed == 1){
                clearInterval(window.intervalid);
                window.checkstarted = "false";
            }
        },
        error: function(jqWHR, textStatus, errorThrown) {
            alert(textStatus);
            alert(errorthrown);
        }
    });
}
/*
function stat_check(num){
    // do ajax get to check status of the job
    var serializedData = $("#form"+num).serialize();
    $.ajax({
        url: "status/"+num+"/"+$("#svctag"+num).val()+"/",
        type: "get",
        data: serializedData,
        cache: 'false',
        dataType: 'json',
        async: 'true',
        success: function(data) {
            //var currentTime = new Date();
            //var hours = currentTime.getHours();
            //var minutes = currentTime.getMinutes();
            //var secs = currentTime.getSeconds();

            // display the status of the job that was returned from the ajax call
            if(document.getElementById('status'+data.num).style.display == 'none'){
                document.getElementById('status'+data.num).style.display = 'inline';
            }
            //$('#status'+data.num).html(data.num+"  "+hours+":"+minutes+":"+secs);
            $('#status'+data.num).html("Step "+data.status+" of "+data.done+" : "+data.message);

            // stop checking the status when the job is complete
            if(data.status == data.done){
            //if(secs > 50){
                clearInterval( $("#form"+data.num).data("mach_info-interval-id"));
            }
        },
        error: function(jqWHR, textStatus, errorThrown) {
            alert(textStatus);
            alert(errorthrown);
        },
    });
}
*/  
function globalOS(os){
    //change all os dropdowns to the same thing
    var checkboxes = document.getElementsByClassName("check");
    for( var i = 0;i<checkboxes.length;i++){
        if(checkboxes[i].checked == true && checkboxes[i].disabled == false){
            var num = checkboxes[i].name.match(/\d+$/)[0];
            $("#os"+num).val($(os).val());
        }
    }
}
function globalProf(prof){
    // change all application profile dropdowns to the same thing
    var checkboxes = document.getElementsByClassName("check");
    for( var i = 0;i<checkboxes.length;i++){
        if(checkboxes[i].checked == true && checkboxes[i].disabled == false){
            var num = checkboxes[i].name.match(/\d+$/)[0];
            $("#app_prof"+num).val($(prof).val());
        }
    }
}

function checkAll(){
    if($('#checkall').is(':checked')){
        $('.check:not(:disabled)').prop('checked',true).change();
    } else {
        $('.check:not(:disabled)').prop('checked',false).change();
    }
}

function deleteJob(del){
    var num = del.name.match(/\d+$/)[0];
    // need to delete machine from the machine table
    // keeping the completed job in the job_tracker table however for documentation purposes
    $.ajax({
        url: "delete/"+num+"/"+$('#svctag'+num).val()+"/",
        type: "get",
        cache: 'false',
        dataType: 'json',
        async: 'true',
        success: function(data) {
            var row = document.getElementById('delete'+data.num).parentNode.parentNode.rowIndex;
            document.getElementById('main').deleteRow(row);
        
        },
        error: function(jqWHR, textStatus, errorThrown) {
            alert(textStatus);
            alert(errorthrown);
        }
    });
}

