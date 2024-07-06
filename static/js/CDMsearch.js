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
console.log("ajax");
$.ajax({
  url:"/CDM/CDM-edit/",
  type:"POST",
  dataType:"json",
  async:true,
  /*data:{project:$('#project').val(),Phase:$('#Phase').val(),csrfmiddlewaretoken:'{{ csrf_token  }}'},*/
  data:{Customer:$('#Customer').val(),project:$('#Project').val(),C_cover_Material:$('#C_cover_Material').val(),D_cover_Material:$('#D_cover_Material').val(),csrfmiddlewaretoken:$("input:first").val(),Search:""},
  /*header:{'X-CSRFtoken':csrftoken},*/
  success:function(data){
      //console.log("750");
      //console.log(data);

    //$('#TableSize').empty();
    //$("#TableSize").append("<table  border='3' cellpadding='0' cellspacing='0' id='table' freezeRowNum='1' freezeColumnNum='1' overflow='scroll' class=table7_7></table>");
      //line(data);
      console.log(data == null);


  },
  error:function(data){
    alert("未查询到数据，请确认查询信息");
    console.log("fail");
  }
})
});

