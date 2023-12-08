// Function that gets the JSON data from the server
// and returns it as a JSON object

// function get_json() {
//   var json = null;
//   $.ajax({
//     url: "https://adventofcode.com/2023/leaderboard/private/view/954860.json",
//     dataType: "json",
//     crossDomain: true,
//     setCookies:
//       "session=53616c7465645f5f1c43c14b203359c399a1c7373e63dd4884a54869a787103f3b76a8df0dbcfcab49920c81cd573200b657ea0016db75fb023f35c8ed37264e",
//     xhrFields: {
//       withCredentials: true,
//     },
//     success: function (data) {
//       json = data;
//     },
//   });
//   return json;
// }

function get_json() {
  let headers = new Headers();
  headers.append("Access-Control-Allow-Origin", "http://localhost:3000");
  headers.append("Access-Control-Allow-Credentials", "true");
  headers.append("Access-Control-Allow-Methods", "GET");
  headers.append("Access-Control-Allow-Headers", "Content-Type");
  headers.append(
    "Cookie",
    "session=53616c7465645f5f1c43c14b203359c399a1c7373e63dd4884a54869a787103f3b76a8df0dbcfcab49920c81cd573200b657ea0016db75fb023f35c8ed37264e"
  );
  fetch("https://adventofcode.com/2023/leaderboard/private/view/954860.json", {
    method: "GET",
    headers: headers,
    mode: "no-cors",
  })
    .then((response) => {
      console.log(response);
      return response;
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      return data;
    });
}
