function Fileupload (filevalue, filesize, filetype, filecallback) {
    var file = filevalue.files[0];
    var fileSize = (file.size / 1024).toFixed(0);   // 不保留小数  可随意用任何方法  如Math
    var fileType = filevalue.value.substring(filevalue.value.lastIndexOf("."));
// console.log(file+'+-----------------+'+fileSize+'+-----------------+'+fileType);
    if (fileSize > filesize) {
        alert('上传文件超出限制大小（5M）');
        $('#upload-file').val('');
        return false;
    }

    switch (filetype) {
        case 'office':
            if (!fileType.match(/.jpg|.jpeg|.png|.bmp|.gif|.mp4|.wmv|.zip|.7z|.rar|.pdf|.xlsx/i)) {
                alert('请上传jpg、png、jpeg、bmp、gif、mp4、wmv、zip、7z、rar格式文件文件');
                $('#upload-file').val('');
                return false;
            }
            break;
        default:
            alert('filetype参数错误');
            console.error('filetype参数错误！');
            return false;
            break;
    }
    filecallback()
}

    $('#upload-file').change(function () {
        Fileupload(this, 5120, 'office', function () {
            //alert('success 上传成功');
            // console.log($('#upload-file').val());
        })
    })
