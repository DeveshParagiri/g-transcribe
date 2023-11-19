function uploadFile(form)
{
 const formData = new FormData(form);
 var oOutput = document.getElementById("static_file_response")
 var oBody = document.getElementById("form-area")
 var oNewtr = document.getElementById("newtr")
 var oReq = new XMLHttpRequest();
 oReq.open("POST", "upload_static_file", true);
 oReq.onload = function(oEvent) {
     if (oReq.status == 200) {
      const obj = JSON.parse(oReq.response);
      if (oNewtr.style.display === 'none') {
        oNewtr.style.display = 'block';
      }
      oBody.style.visibility = 'hidden';
      oOutput.style.font = 'inherit';
      oOutput.style.fontSize = 'x-large'
      oOutput.innerHTML = obj.text;
      console.log(oReq.response)
     } else {
       oOutput.innerHTML = "An error occurred when trying to transcribe your file.<br \/>";
     }
     };
if (oOutput.style.display === 'none') {
  oOutput.style.display = 'block';
}
 console.log("Processing file!")
 oReq.send(formData);
}