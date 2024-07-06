
var file_xlsx ={} ;


// 监听事件：首先上传，通过监听input的变化，确定是否选择了文件

$("#xlsxUpload").change(function(e){
   // console.log(e.target.files);

   file_xlsx = e.target.files;
   //console.log($(this).val());
   if(($(this).val().slice(-4) === 'xlsx')){
     return file_xlsx ;
   }else{
       if($(this).val()){
          alert('文件类型不正确');
       }
     $(this).val('');
   }
 })

function Upload(e){
  var xlsx_Submit = e.getAttribute("id");
  // console.log(xlsx_Submit);

   var result;
//   var show = document.getElementById(xlsx_Upload)
  // var show =eval($('#xlsxUpload'));
  //  console.log(file)
   let files = file_xlsx;

   if (!files[0]){
      alert("未選擇數據文件"+files[0]);
      return ;
     }
     //针对IE不支持 readAsBinaryString 方法
   if (!FileReader.prototype.readAsBinaryString) {
     //添加原型方法
    FileReader.prototype.readAsBinaryString = function (fileData) {
       var binary = "";
       var pt = this;
       var reader = new FileReader();
       reader.onload = function (e) {
           var bytes = new Uint8Array(reader.result);
           var length = bytes.byteLength;
           for (var i = 0; i < length; i++) {
               binary += String.fromCharCode(bytes[i]);
           }
            //pt.result  - readonly so assign binary
            pt.content = binary;
            pt.onload(pt); //页面内data取pt.content文件内容
            /*pt.content = binary;
            $(pt).trigger('onload');*/

    }
       reader.readAsArrayBuffer(fileData);

    }
   }
   var fileReader = new FileReader ();
   fileReader.onload = function (ev) {
            try {
                var data = (ev.target)?ev.target.result:ev.content,
                    workbook = XLSX.read(data, {
                        type: 'binary'
                    }), // 以二进制流方式读取得到整份excel表格对象
                    persons = []; // 存储获取到的数据

            } catch (e) {

                return;
            }
            for (var sheet in workbook.Sheets) {
                if (workbook.Sheets.hasOwnProperty(sheet)) {
                    var fromTo = workbook.Sheets[sheet]['!ref'];
                    // console.log(fromTo);
                    var datas = workbook.Sheets[sheet];

                    // 如果有不规范数据可以在这里进行处理datas

                    persons = persons.concat(XLSX.utils.sheet_to_json(datas));
                    //break; // 只读了第一张表

                }
            }
            // console.log(JSON.stringify(persons));
            result=JSON.stringify(persons);
             //上傳數據
             //    console.log(result,window.location.pathname);
                $.ajax({
                  url:window.location.pathname,
                  type:"POST",
                  dataType:"json",
                  async:true,
                  /*data:{project:$('#project').val(),Phase:$('#Phase').val(),csrfmiddlewaretoken:'{{ csrf_token  }}'},*/
                  //data:{Customer:$('#Customer').val(),project:$('#project').val(),Phase:$('#Phase').val(),csrfmiddlewaretoken:$("input:first").val(),},
                  data:{type:"xlsx",upload:result,csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val()},
                  /*header:{'X-CSRFtoken':csrftoken},*/
                  success:function(data){
                     /*console.log(data.err_ok == 1);*/
                      // console.log(data.content,'contend');
                     if(data.err_ok == 1){
                          // console.log(typeof(data.content),'contend');
                       //this.getData = data.content;
                       //document.getElementById("msgContent").innerHTML+="<table>";
                       var Table ;
                       /*console.log(this.getData);*/
                       Table = "<table>";
                       for(var items=0 ;items < data.content.length;items++){

                         //document.getElementById("msgContent").innerHTML+="<tr>";
                         Table += "<tr>";
                         // console.log(data.content[items]);
                         for(var item in data.content[items]){

                            //document.getElementById("msgContent").innerHTML+="<td>"+this.getData[items][item]+"</td>";
                            Table += "<td>"+data.content[items][item]+"</td>";
                          }

                         //document.getElementById("msgContent").innerHTML+="</tr>";
                         Table += "</tr>";
                       }
                       //document.getElementById("msgContent").innerHTML+="</table>";
                       Table += "</table>";
                       document.getElementById("msgContent").innerHTML=Table;
                       /*$("#msgContent").append('<span>'+data.content+'</span>');*/
                         // console.log(Table);
                       console.log($('#returnMsg'));
                       $("#returnMsg").modal('show');
                       $('#returnMsg').on('hidden.bs.modal', function () {

                            $("#msgContent").empty();

                          })
                     }else if(data.err_ok == 0){
                        alert("上傳成功！");
                     }

                  },
                  error:function(data){
                       alert("上傳失敗");
                  }
                })
        };
        try{
            fileReader.readAsBinaryString(files[0]);
           }
        catch(e){
          alert("文件上傳異常") ;

          return;
        }
        $('#xlsxUpload').val('');


}


