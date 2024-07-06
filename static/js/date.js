var year,month,day,hours,minutes,seconds,milliseconds;
/*window.onload=function(){setInterval(function(){date();},1000)
    
	}*/

	function date(){
	var time= new Date();
    year=time.getFullYear();
    month=time.getMonth()+1;
    day=time.getDate();
    hours=time.getHours();
    minutes=time.getMinutes();
    seconds=time.getSeconds();
	/*console.log(fnW(day)+'/'+fnW(month)+'/'+year+' '+fnW(hours)+':'+fnW(minutes)+':'+fnW(seconds));*/
	document.getElementById('time').innerHTML=fnW(day)+'/'+fnW(month)+'/'+year+' '+fnW(hours)+':'+fnW(minutes)+':'+fnW(seconds);
	}
	
	function fnW(str){
		var num;
		str>9?num=str:num="0"+str;
		return num;
	} 

	$(document).ready(function(){

　　setInterval(function(){date();},1000);

});
