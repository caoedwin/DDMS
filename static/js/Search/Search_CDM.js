
/*Test Data 
*/

/*var JSONObject={{JSONObject|safe}};*/
/*Test Data End*/
/*function $$(id){
return document.getElementById(id);
}*/
//Item ID 字典
var coldata={};

function $$(id){
        return document.getElementById(id);
        }
 
let i = 0, j = 0;
let ItemNum =0;
/*生成表格函数->for 避免表格鼠标悬浮窗不随滚动条变化*/
function CreateTable(row,col,mouse,column){
   var tab = "";
   for(let i=0;i<row;i++){
          if(i==0){
            tab+="<thead><tr>"
          }

          
          if(i!=0){
          tab += "<tr >"} 
           for(let j=0;j<col;j++){


             var xuhao = ('x'+i+'y'+j).toString();
               ItemNum=(i*row+j);
                /*console.log(xuhao);*/
                  //这里加入了id 排好了序
                if(i==0||j==0){
                  if(j==0){
                      if(i==0&&j==0){
                        tab+="<th id="+xuhao+" style='min-width:150px;height:50px;'></td>";
                        continue;
                      }
                      tab+="<th id="+xuhao+column+" style='width:150x;height:50px;max-height:50px;word-wrap:break-word;'"+mouse+"></th>";
                       continue;
                      }
                  tab+="<th id="+xuhao+" style='min-width:150px;'></th>";
                  continue;
               
                  }
                  tab+="<td id="+xuhao+" ></td>";
              }
                 if(i==0){
                 tab+="</tr></thead>"
           }
                if(i>=1&&i<(row-1)){
                 tab += "</tr>"}
                if(i==(row-1)){
                  tab += "</tr>"
                }
            }
            return tab;
}

/*函数结束*/



 function line(JSONObject){
       
       /* console.log("line");*/
        /*显示指定行列*/

       //删除上次存下来的item id
       

         for (var key in coldata) {
               delete coldata[key];
            };


        $("table").empty();
        var row=(getjsonlength(JSONObject)>10)?getjsonlength(JSONObject):10,col=totaltime(JSONObject.time[0].starttime,JSONObject.time[0].endtime)+1;  //获取行列的长度的变量
        var table_1=$('#table').clone(true);
        //console.log(row,col);
       /* console.log(table_1);*/
        var tab=CreateTable(row,col,' ','');
        var tab1=CreateTable(row,col,"onmouseout=out(this) onmouseover=over(this)","col");
        
            table_1.attr("id","table_1");
            $$("table").innerHTML = tab;
           
            
            table_1.append(tab1);
            

            
            /*显示结束*/



           /* fixtable start*/


            /* $(document).ready(function(){*/
              var table = $("table");
             /* var table_col = $("#table_1");*/
              var tableId = table.attr('id');
              var tableId_col = table_1.attr('id');
              var freezeRowNum = table.attr('freezeRowNum');
              var freezeColumnNum = table.attr('freezeColumnNum');
              
              /*根据屏幕缩放改变的table大小*/
             

                 

              /*根据屏幕缩放改变的table大小--结束*/
              
              if (typeof(freezeRowNum) != 'undefined' || typeof(freezeColumnNum) != 'undefined') {
                  freezeTable(table,table_1,tableId_col, freezeRowNum || 0, freezeColumnNum || 0, $('#TableSize').outerWidth(true), $('#TableSize').outerHeight(true));
                 /* console.log($('#TableSize').outerHeight(true),$('#TableSize').outerWidth(true),$('#table_tableData').outerHeight(true),$('#table_tableData').outerWidth(true));*/
                  var flag = false;
               
              }
              var title0="<div style='width: 100%;height:50px;backgound-color:#B0C4DE;'><canvas style='width: 100%;height: 100% ;backgound-color:#FFDC35'id='mycanvas' cellpadding='0'cellspacing='0'></canvas></div>"
                     ;
                     /* $('#table').fixedHeaderTable({});*/
                      $$("x0y0").innerHTML = title0;

                      

                      var myCanvas = document.getElementById("mycanvas");
                      var width = myCanvas.width;
                      var height = myCanvas.height;
                      var ctx = myCanvas.getContext("2d");
                      ctx.strokeStyle="#000";
                      ctx.lineWidth=2;
                      
                      ctx.moveTo(0,0);
                      ctx.lineTo(width,height);
                      ctx.stroke();
               
                      ctx.font="40px bold SimHei";
                      ctx.fontheight="bold";
                      ctx.fillText("Date",width/3*1.8,height*5/12);
                      ctx.fillText("Units",width/9,height/5*4);

                      //数据渲染
                      //console.log(JSONObject.time[0].endtime);
                      var num=1;
                      for(var i=1;i<col;i++)//date
                      {
                        /*console.log(days(JSONObject.starttime,JSONObject.endtime)[i]);*/
                        var daysdate=days(JSONObject.time[0].starttime,JSONObject.time[0].endtime)[i-1];

                        var newdaysdate=daysdate.split("/");
                        var newdate= new Date();
                        newdate.setFullYear(newdaysdate[0],newdaysdate[1]-1,newdaysdate[2]);
                        week=newdate.getDay();//week.getDay();
                        var date1=$("#x0y"+i).attr("id");
                        ;

                        /*console.log(eval(date1));*/

                        $(eval(date1)).append("<span><center>"+daysdate+"</center></span>");
                        if(week==0||week==6){
                           //console.log("0-6");
                           $(eval(date1)).css({"background": "rgba(119,136,153,0.5)"});
                          // console.log($(eval(date1)).attr("style"));
                        }
                        //console.log(JSONObject.time[0].starttime,JSONObject.time[0].endtime);
                      }



                      for(var i in JSONObject){  //遍历units
                       // console.log(JSONObject[i]);
                        if (i!="time"){
                           var startflag=[];
                           var k=0;
                           var m=0;
                            for(var j=0;j<JSONObject[i].length;j++){ //遍历JSON数据中的数组

                              //console.log(gettime(JSONObject[i][j].starttime,JSONObject[i][j].endtime));
                             // console.log($(eval($("#x"+num+"y0col").attr("id"))).children().length);
                              if($(eval($("#x"+num+"y0col").attr("id"))).children().length<=0){ //判断是否有子节点，避免重复赋值
                                $(eval($("#x"+num+"y0col").attr("id"))).append("<span><center>"+getunit(i)+"</center></span>");

                              }

                              //s:以starttime开始的第几天
                              var s=totaltime(JSONObject.time[0].starttime,getdate(JSONObject[i][j].starttime));
                              //e:测试历经的天数
                              var e=(JSONObject[i][j].endtime=="")?(totaltime(getdate(JSONObject[i][j].starttime),JSONObject.time[0].endtime)):(totaltime(getdate(JSONObject[i][j].starttime),getdate(JSONObject[i][j].endtime)));
                              if(JSONObject[i][j].endtime==""){
                                JSONObject[i][j].endtime=JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59";
                              }

                              startflag[k]=s;
                              m+=e;    //重合需合并之前的e
                              //console.log(j,JSONObject[i][j].endtime,JSONObject[i][j+1].starttime);
                              if(j<(JSONObject[i].length-1)&&getdate(JSONObject[i][j].endtime)==getdate(JSONObject[i][j+1].starttime)){
                                k++;
                              }
                              else{
                                 //console.log(k);
                               if(m-k>1&&JSONObject[i][j].endtime!=null){ //隐藏被合并的单元格，当没有合并单元格不生效
                                 for(var index=1;index<m-k;index++ ){
                                  $(eval($("#x"+num+"y"+(startflag[0]+index)).attr("id"))).css({"display":"none"});
                                }
                               }


                                   //$(eval($("#x"+num+"y"+startflag[0]).attr("id"))).css({"background-color":"red"});//设置测试标记的背景色
                                   $(eval($("#x"+num+"y"+startflag[0]).attr("id"))).attr("colSpan",m-k); //合并的列数
                                   var progressbar;
                                   for(var f =0;f<=k;f++){
                                    //console.log(f);
                                    //console.log(JSONObject[i][j].endtime+"4");
                                     var rgba;
                                     if(JSONObject[i][j].endtime==JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59"&&k==f){
                                         rgba="(255,165,0,0.6)";
                                      }
                                    if(f==0){
                                      var rgba=(JSONObject[i][j-k].Result=="Pass")?"(113,198,113,0.8)":"(195,33,54,0.8)";
                                      if(JSONObject[i][j].endtime==JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59"&&k==f){
                                         rgba="(255,165,0,0.6)";
                                      }
                                      if(JSONObject[i][j-k].RD==1){
                                          rgba="(207,207,207,1)";
                                      }
                                      var unfinish=JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59";
                                      var end=(JSONObject[i][j-k].endtime==unfinish)?"今（未完成）":JSONObject[i][j-k].endtime;
                                      var spendtime=(JSONObject[i][j-k].endtime==unfinish)?"Testing":gettime(JSONObject[i][j-k].starttime,JSONObject[i][j-k].endtime)+" mins";
                                      progressbar="<div  role='progressbar' style='width:"+((getstarttime(JSONObject[i][j-k].starttime)*100)/((m-k)*24*60))+"%' ><span></span></div><div  value='测试时间："+JSONObject[i][j-k].starttime+"至"+end+" &#010 测试用时："+spendtime+"&#010 测试结果："+JSONObject[i][j-k].Result+" &#010 测试项目："+JSONObject[i][j-k].des+"' role='progressbar' style='position: relative;border-radius:4px;flex-direction:column;justify-content:center;display:flex;text-align:center;color:#fff;width:"+((gettime(JSONObject[i][j-k].starttime,JSONObject[i][j-k].endtime)*100)/((m-k)*24*60))+"%;background-color:rgba"+rgba+"'id='x"+num+"y"+startflag[0]+"z"+f+"' data-toggle='tooltip' class='pb' onmouseout=tipout(this) onmouseover=tipover(this) name='' z-index=1001></div>";
                                      //console.log((getstarttime(JSONObject[i][j-k].starttime)*100),f);

                                    }else{
                                      var rgba=(JSONObject[i][j-k+f].Result=="Pass")?"(113,198,113,0.8)":"(195,33,54,0.8)";
                                      if(JSONObject[i][j].endtime==JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59"&&k==f){
                                         rgba="(255,165,0,0.6)";
                                      }
                                       if(JSONObject[i][j-k+f].RD==1){
                                          rgba="(207,207,207,1)";
                                      }
                                      //console.log("end214",JSONObject[i][j-k+f].endtime,JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59");
                                      var unfinish=JSONObject.time[0].endtime.slice(0,4)+"-"+JSONObject.time[0].endtime.slice(4,6)+"-"+JSONObject.time[0].endtime.slice(6,8)+" 23:59:59";
                                      var spendtime=(JSONObject[i][j-k+f].endtime==unfinish)?"Testing":gettime(JSONObject[i][j-k+f].starttime,JSONObject[i][j-k+f].endtime)+" mins";
                                      var end=(JSONObject[i][j-k+f].endtime==unfinish)?"今（未完成）":JSONObject[i][j-k+f].endtime;
                                     //var end="in";
                                      progressbar+="<div  role='progressbar'z-index=1000 style='width:"+((gettime(JSONObject[i][j-k+f-1].endtime,JSONObject[i][j-k+f].starttime)*100)/((m-k)*24*60))+"%' ><span></span></div><div class='pb' z-index=1000 role='progressbar' style='border-radius:4px;flex-direction:column;justify-content:center;display:flex;text-align:center;color:#fff;width:"+((gettime(JSONObject[i][j-k+f].starttime,JSONObject[i][j-k+f].endtime)*100)/((m-k)*24*60))+"%;position:relative;background-color:rgba"+rgba+"' z-index=1000 id='x"+num+"y"+startflag[0]+"z"+f+"'  onmouseout=tipout(this) onmouseover=tipover(this)  value='"+JSONObject[i][j-k+f].starttime+"至"+end+" &#010 测试用时："+spendtime+"　&#010 测试结果："+JSONObject[i][j-k+f].Result+" &#010 测试项目："+JSONObject[i][j-k+f].des+"' name='' ></div>";
                                      //console.log((gettime(JSONObject[i][j-k+f-1].endtime,JSONObject[i][j-k+f].starttime)*100),f);

                                      }
                                   }
                                   $(eval($("#x"+num+"y"+startflag[0]).attr("id"))).append("<div   style='height:100%;display:flex'>"+progressbar+"</div>");
                                   //console.log(JSONObject[i][j].des);
                                   startflag.splice(0,startflag.length);//清空startflag数组
                                   k=0;//合并计数清空
                                   m=0;//合并display的天数
                               }
                            }
                        }
                        num++;
                      }



                        //渲染结束
                        /*$(eval($("#x2y3").attr("id"))).css({"display":"none"});*/


                  /*测试数据*/
           /* for(var i in JSONObject){
             //操作范围：非x,y(行列值)，非x0y0
              if(i!='x'&&i!='y'&&i.toString().slice(0,3)!="x0y0"){
                if(i.toString().slice(2,4)=="y0"){

                    i_col=$("#"+i).attr("id");


                  $(eval(i_col+"col")).append("<center><span>"+JSONObject[i].slice(11)+"</span></center>");//获取数据11位之后的字符
                  coldata[i_col+"col"]=JSONObject[i].slice(0,11);
                   $$(i_col.toString()).innerHTML="<center><span>"+JSONObject[i]+"</span></center>";
                  }

                else{
                     console.log(i.toString().slice(1,2));


                     $(eval(i)).append("<center><span>"+JSONObject[i]+"</span></center>");
                       if (JSONObject[i]>=5&&i.toString().slice(1,2)!="0"){
                         $(eval(i)).css({"background": "red"});
                     }


                 }
              }
            }*/


        }
        /*
 * 锁定表头和列
 *
 * 参数定义
 *     table - 要锁定的表格元素或者表格ID
 *     freezeRowNum - 要锁定的前几行行数，如果行不锁定，则设置为0
 *     freezeColumnNum - 要锁定的前几列列数，如果列不锁定，则设置为0
 *     width - 表格的滚动区域宽度
 *     height - 表格的滚动区域高度
 */
function freezeTable(table,table_col,tableId_col,freezeRowNum, freezeColumnNum, width, height) {

    if (typeof(freezeRowNum) == 'string')
        freezeRowNum = parseInt(freezeRowNum)

    if (typeof(freezeColumnNum) == 'string')
        freezeColumnNum = parseInt(freezeColumnNum)

    var tableId;
    if (typeof(table) == 'string') {
        tableId = table;
        table = $('#' + tableId);
    } else
        tableId = table.attr('id');



    var divTableLayout = $("#" + tableId + "_tableLayout");

        table.after("<div id='" + tableId + "_tableLayout' style='overflow-x:auto;height:" + $('#TableSize').outerHeight(true) + "px; width:" + width + "px;'  ></div>");

        divTableLayout = $("#" + tableId + "_tableLayout");


    var html = '';
    if (freezeRowNum > 0 && freezeColumnNum > 0)
        html += '<div id="' + tableId + '_tableFix" style="padding: 0px;height:60px;"></div>';

    if (freezeRowNum > 0)
        html += '<div id="' + tableId + '_tableHead" style="padding: 0px;"></div>';

    if (freezeColumnNum > 0)
        html += '<div id="' + tableId + '_tableColumn" style="padding: 0px;"></div>';

    html += '<div id="' + tableId + '_tableData" style="padding: 0px;"></div>';


    $(html).appendTo("#" + tableId + "_tableLayout");

    var divTableFix = freezeRowNum > 0 && freezeColumnNum > 0 ? $("#" + tableId + "_tableFix") : null;
    var divTableHead = freezeRowNum > 0 ? $("#" + tableId + "_tableHead") : null;
    var divTableColumn = freezeColumnNum > 0 ? $("#" + tableId + "_tableColumn") : null;
    var divTableData = $("#" + tableId + "_tableData");
    //console.log(table);
    //console.log(table_col);
    divTableData.append(table);

    if (divTableFix != null) {
        var tableFixClone = table.clone(true);
        tableFixClone.attr("id", tableId + "_tableFixClone");
       /* console.log(tableFixClone);*/
        divTableFix.append(tableFixClone);
    }

    if (divTableHead != null) {
        var tableHeadClone = table.clone(true);
        tableHeadClone.attr("id", tableId + "_tableHeadClone");

        divTableHead.append(tableHeadClone);
    }

    if (divTableColumn != null) {
        var tableColumnClone =  table_col.clone(true);
        tableColumnClone.attr("id", tableId + "_tableColumnClone");
       /* console.log(tableColumnClone);*/
        divTableColumn.append(tableColumnClone);
        /*console.log(document.getElementsByTagName("#tableColumnClone"));*/
    }

    $("#" + tableId + "_tableLayout table").css("margin", "0");

    if (freezeRowNum > 0) {
        var HeadHeight = 0;
        var ignoreRowNum = 0;
        $("#" + tableId + "_tableHead tr:lt(" + freezeRowNum + ")").each(function () {
            if (ignoreRowNum > 0)
                ignoreRowNum--;
            else {
                var td = $(this).find('td:first, th:first');
                HeadHeight += td.outerHeight(true);

                ignoreRowNum = td.attr('rowSpan');
                if (typeof(ignoreRowNum) == 'undefined')
                    ignoreRowNum = 0;
                else
                    ignoreRowNum = parseInt(ignoreRowNum) - 1;
            }
        });
        HeadHeight += 2;

        divTableHead.css("height", HeadHeight);
        divTableFix != null && divTableFix.css("height", HeadHeight);
    }

    if (freezeColumnNum > 0) {
        var ColumnsWidth = 0;
        var ColumnsNumber = 0;
        $("#" + tableId + "_tableColumn tr:eq(" + freezeRowNum + ")").find("td:lt(" + freezeColumnNum + "), th:lt(" + freezeColumnNum + ")").each(function () {
            if (ColumnsNumber >= freezeColumnNum)
                return;

            ColumnsWidth += $(this).outerWidth(true);

            ColumnsNumber += $(this).attr('colSpan') ? parseInt($(this).attr('colSpan')) : 1;
        });
        ColumnsWidth += 2;

        divTableColumn.css("width", ColumnsWidth);
        divTableFix != null && divTableFix.css("width", ColumnsWidth);
    }

    divTableData.scroll(function () {
        divTableHead != null && divTableHead.scrollLeft(divTableData.scrollLeft());

        divTableColumn != null && divTableColumn.scrollTop(divTableData.scrollTop());

    });

    var srollwidth=(myBrowser()=="Chrome")?(window.innerWidth - document.body.clientWidth):17;
    divTableFix != null && divTableFix.css({ "overflow": "hidden", "position": "absolute", "z-index": "50" });
    divTableHead != null && divTableHead.css({ "overflow": "hidden","height":$('#table_tableFix').outerHeight(true), "width": $('#TableSize').outerWidth(true)-srollwidth, "position": "absolute", "z-index": "45" });
    divTableColumn != null && divTableColumn.css({ "overflow": "hidden", "height": $('#TableSize').outerHeight(true)-srollwidth,"width":$('#table_tableFix').outerWidth(true), "position": "absolute", "z-index": "40" });
    divTableData.css({ "overflow": "auto", "width":$('#TableSize').outerWidth(true), "height": $('#TableSize').outerHeight(true), "position": "absolute" });
    /*console.log(width,height);*/

    divTableFix != null && divTableFix.offset(divTableLayout.offset());
    divTableHead != null && divTableHead.offset(divTableLayout.offset());
    divTableColumn != null && divTableColumn.offset(divTableLayout.offset());
    divTableData.offset(divTableLayout.offset());
    /*console.log(tableHeadClone)*/


}




    /*鼠标悬停功能之units*/
      var differentindex=999;

      function openMsg(obj) {

         /* differentindex = layer.tips(coldata[obj],"#"+obj,
           {tips: [4, "#4794ec"]
         });*/
        }


     function over(obj){
      if($("#"+obj.id).children().length>0){    //判断是否存在子节点（若有子节点，显示悬浮窗，反之则无）
            openMsg(obj.id);
           //console.log(obj.id);
          }
     }
     function out(obj){
        layer.close(differentindex);
     }

     function tipover(obj){
      //$("#tip").empty();

      //console.log(event.clientX,event.clientY,obj);
      $(obj).mousemove(function(e){
      $("#tip").css({"display":"block","left":(event.clientX+10)+"px","top":(event.clientY+15)+"px","z-index":"9999"});
      console.log("578",$(obj).attr("value"));
      $("#tip").text($(obj).attr("value"));
        });
      }

     function tipout(){
      console.log("out");
      $("#tip").css({"display":"none"});
      $("#tip").empty();
     }


//鼠标悬浮框之测试记录的详细信息
function newopenMsg(obj) {
          var msg=$("#"+obj).attr("value")+" "+$("#"+obj).attr("name");
          $("#"+obj).focus()
          differentindex = layer.tips(msg,"#"+obj,
           {tips: [2, "#4794ec"],
           //area: ['auto','auto'],
           time: 20000,

         });
        }


     function newover(obj){
      /*if($("#"+obj.id).children().length>0){    //判断是否存在子节点（若有子节点，显示悬浮窗，反之则无）
            newopenMsg(obj.id);
           console.log(obj.id);
          }*/
           newopenMsg(obj.id);
           //console.log(obj.id);
     }
     function newout(obj){
        layer.close(differentindex);
     }





//newover
//chrome or ie
    function myBrowser(){

    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
        //console.log(userAgent);

    var isOpera = userAgent.indexOf("Opera") > -1;

    if (isOpera) {

        return "Opera"

    }; //判断是否Opera浏览器

    if (userAgent.indexOf("Firefox") > -1) {

        return "FF";

    } //判断是否Firefox浏览器

    if (userAgent.indexOf("Chrome") > -1&&userAgent.indexOf("Edge") <= -1){

        return "Chrome";

    }
    if (userAgent.indexOf("Edge") > -1){

        return "Edge";

    }

    if (userAgent.indexOf("Safari") > -1) {

        return "Safari";

    } //判断是否Safari浏览器

    if (userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera) {

        return "IE";

    }; //判断是否IE浏览器

}

//bootstrap 悬停



      /*鼠标悬停功能*/
    //判断是否为闰年
    function years(year){
      var y=0;
      if ((year%4==0&&year%100!=0)||year%400==0){
          y=1;
      }
      return y;
    }
    //判断该月的天数
    function months(year,month){
      var day;
     /* console.log(month);*/
      switch (month){
        case 1:
        case 3:
        case 5:
        case 7:
        case 8:
        case 10:
        case 12:day=31;
                break;
        case 4:
        case 6:
        case 9:
        case 11:day=30;
                 break;
        case 2: day=(years(year)==1)?29:28;

      }
      return day;
    }
    //相隔月份的天数
    function middletime(year,startmonth,endmonth){

      var y=endmonth;
      var day=0;

      for(var x=startmonth+1;x<y;x++){
        day +=months(year,x);
      }
      return day;
    }
    //总共相差的天数(包含第一天)
    function totaltime(starttime,endtime){
       var year_start=parseInt(starttime.toString().slice(0,4));
       var year_end=parseInt(endtime.toString().slice(0,4));
       var month_start=parseInt(starttime.toString().slice(4,6));
       var month_end=parseInt(endtime.toString().slice(4,6));
       var day_start=parseInt(starttime.toString().slice(6,8));
       var day_end=parseInt(endtime.toString().slice(6,8));
       var test_day;
       /*console.log(year_start,year_end,month_start,month_end,day_start,day_end);*/

       if(month_start==month_end){
        //第一种情况：测试开始时间与结束时间在同一月
         test_day=day_end-day_start+1;


       }
       else if(month_start<month_end){
              //第二种情况：测试开始时间与结束时间不在同一月，但并未跨年
              test_day=(months(year_start,month_start)-day_start+1)+middletime(year_start,month_start,month_end)+day_end;

              }
            else{
              //第三种情况：测试时间与结束时间不在同一月，而且出现跨年
                test_day=(months(year_start, month_start)-day_start+1)+middletime(year_start,month_start,13)+middletime(year_end,0,month_end)+day_end;

                }
                return test_day;
    }
    //产生所有日期的数组
    function days(starttime,endtime){
      var year_start=parseInt(starttime.toString().slice(0,4));
       var year_end=parseInt(endtime.toString().slice(0,4));
       var month_start=parseInt(starttime.toString().slice(4,6));
       var month_end=parseInt(endtime.toString().slice(4,6));
       var day_start=parseInt(starttime.toString().slice(6,8));
       var day_end=parseInt(endtime.toString().slice(6,8));
       var day= new Array();
       day[0]=year_start+'/'+month_start+'/'+day_start;
       for(x=1;x<totaltime(starttime,endtime);x++){//根据计算出来的相差天数，依次加1
          day_start++;

          if(day_start>months(year_start,month_start)){//判断超过当月数，产生进位
            month_start++;
            day_start=1;
            if(month_start>12){
             year_start++;
             month_start=1;
             day_start=1;
            }
          }

       day[x]=year_start+'/'+month_start+'/'+day_start;

       }
      /* console.log(totaltime(starttime,endtime));*/
      return day;
    }
    //对数据库的date值进行处理
    function getdate(starttime){
       var year=starttime.toString().slice(0,4);

       var month=starttime.toString().slice(5,7);

       var day=starttime.toString().slice(8,10);

       return (year+month+day);

    }
    //获取json数据的长度
    function getjsonlength(json){
      var l=0;
      for(var i in json){
        l++;
      }
      return l;
    }
    //获取units
    function getunit(unit){
      return parseInt(unit.slice(1,3))+"#"+parseInt(unit.slice(4));
    }
    function gettime(starttime,endtime){
      var starthour=parseInt(starttime.toString().slice(11,13));
      var endhour=parseInt(endtime.toString().slice(11,13));
      var startminute=parseInt(starttime.toString().slice(14,16));
      var endminute=parseInt(endtime.toString().slice(14,16));
      var days =totaltime(getdate(starttime),getdate(endtime))-1;
      //console.log(starthour,endhour,startminute,endminute,days);
      //若days=0 则说明两个时间点在同一天，比较具体时间（小时和分钟）
      if (days==0){
        if(startminute<endminute){
          return (days*24*60+(endhour-starthour-1)*60+(endminute+60-startminute));
        }else{
           return (days*24*60+(endhour-starthour)*60+(endminute-startminute));
        }
      }
      //若days>0 则两个时间点超过一天，可能需要天数借位，即进行每个值比较
      else if(days>0){
        if(starthour>endhour){
          if(startminute>endminute){

             return ((days-1)*24*60+(endhour-starthour+23)*60+(endminute+60-startminute));
           }else if(startminute<=endminute){

             return ((days-1)*24*60+(endhour-starthour+24)*60+(endminute-startminute));
           }
        }else if(starthour<endhour){
          if(startminute>endminute){
            //return
             return (days*24*60+(endhour-starthour-1)*60+(endminute+60-startminute));
          }else if(startminute<=endminute){
            //return
             return (days*24*60+(endhour-starthour)*60+(endminute-startminute));
          }
        }else if(starthour=endhour){
          if(startminute>endminute){
            //return
            return ((days-1)*24*60+(endhour-starthour+23)*60+(endminute+60-startminute));
          }else if(startminute<=endminute){
            //return
            return (days*24*60+(endhour-starthour)*60+(endminute-startminute));
          }
        }
      }
    }
    function getstarttime(starttime){
      var starthour=parseInt(starttime.toString().slice(11,13));
      var startminute=parseInt(starttime.toString().slice(14,16));
      //console.log(startminute,starthour,starthour*60+startminute);
      return starthour*60+startminute;
    }

$(document).ready(function(){

//$(function () { $(".tooltip-options").tooltip({html : true });});


/*$(function () { $(".tooltip.options").tooltip({html : true });
                console.log("Header21s");
                });*/



/*console.log(months(2020,2));*/

$(window).resize(function(){
    var myBrowsertype =myBrowser();
    if(myBrowsertype=="Chrome"){
      var scrollwidth=window.innerWidth - document.body.clientWidth;
      $('#table_tableHead').css({"width":$('#TableSize').outerWidth(true)-scrollwidth});
      $('#table_tableColumn').css({"height":$('#TableSize').outerHeight(true)-scrollwidth});
      $('#table_tableData').css({"width":$('#TableSize').outerWidth(true)});
      $('#table_tableData').css({"height":$('#TableSize').outerHeight(true)});
      //console.log("Chrome",scrollwidth);
    }
    else{
      $('#table_tableHead').css({"width":$('#TableSize').outerWidth(true)-17});
      $('#table_tableColumn').css({"height":$('#TableSize').outerHeight(true)-17});
      $('#table_tableData').css({"width":$('#TableSize').outerWidth(true)});
      $('#table_tableData').css({"height":$('#TableSize').outerHeight(true)});
      //console.log("ie");
    }
     /* console.log($('#TableSize').outerHeight(true),$('#TableSize').outerWidth(true),$('#table_tableData').outerHeight(true),$('#table_tableData').outerWidth(true),$('#table_tableFix').outerHeight(true),);
      */
    });

/*
 * 调整锁定表的宽度和高度，这个函数在resize事件中调用
 *
 * 参数定义
 *     table - 要锁定的表格元素或者表格ID
 *     width - 表格的滚动区域宽度
 *     height - 表格的滚动区域高度
 */
function adjustTableSize(table, width, height) {
    var tableId;
    if (typeof(table) == 'string')
        tableId = table;
    else
        tableId = table.attr('id');

    $("#" + tableId + "_tableLayout").width(width).height(height);
    $("#" + tableId + "_tableHead").width(width );
    $("#" + tableId + "_tableColumn").height(height);
    $("#" + tableId + "_tableData").width(width).height(height);
}



$('#tt').bind('click', function() {
   /* e.preventDefault();*/
    /*console.log(JSONObject);*/
    //console.log("123");
   /* var csrftoken = $.cookie('csrftoken');*/
   /* $('#TableSize').empty();
    $("#TableSize").append("<table  border='3' cellpadding='0' cellspacing='0' id='table' freezeRowNum='1' freezeColumnNum='1' overflow='scroll' ></table>");
      line(); */

  /* if($('#table_tableLayout'))

    */
   /* $('#table_tableLayout').empty();*/

/*AJAX Data*/
/*界面初始化*/

/*局部提交，刷新表格数据*/

$.ajax({
  url:window.location.pathname,
  type:"POST",
  dataType:"json",
  async:true,
  /*data:{project:$('#project').val(),Phase:$('#Phase').val(),csrfmiddlewaretoken:'{{ csrf_token  }}'},*/
  data:{Customer:$('#Customer').val(),Project:$('#Project').val(),SKU_NO:$('#SKU_NO').val(),C_cover_Material:$('#C_cover_Material').val(),D_cover_Material:$('#D_cover_Material').val(),csrfmiddlewaretoken:$("input:first").val(),Search:""},
  /*header:{'X-CSRFtoken':csrftoken},*/
  success:function(data){
      //console.log("750");
      //console.log(data);
     


     
      
  },
  error:function(data){
    alert("未查询到数据，请确认查询信息");
  }
})

/*AJAX Data*/
/*表格自适应大小*/

/*表格自适应大小*/


   
  });

});
  

/*Test*/




/*Test End
*/

