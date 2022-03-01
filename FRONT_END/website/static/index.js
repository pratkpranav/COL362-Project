function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function executefollow(profile_handle) {
  var follow_link, profile_link;
  follow_link = `${window.follow_link}`;
  profile_link = `${window.profile_link}`;
  fetch(follow_link, {
    method: "GET",
  }).then((_res) => {
    window.location.href = profile_link;
  });
}

function executeunfollow(profile_handle) {
  var unfollow_link, profile_link;
  unfollow_link = `${window.unfollow_link}`;
  profile_link = `${window.profile_link}`;
  fetch(unfollow_link, {
    method: "GET",
  }).then((_res) => {
    window.location.href = profile_link;
  });
}

/*Taken from internet*/
function search_country() {
  var input, filter, a, i;
  input = document.getElementById("country_input");
  filter = input.value.toUpperCase();
  div = document.getElementById("country_dropdown");
  a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}

function showTags() {
  document.getElementById("panel").style.display = "block";
}

function add_problem() {
  var tbody = document.querySelector("tbody");
  var template = document.querySelector("#new_problem");
  //var template = $("#new_problem").html();
  //console.log(template);
  var clone = template.content.cloneNode(true);
  var td = clone.querySelectorAll("td");
  var num = document.getElementsByTagName("tr").length + 1;
  var num_row = String.fromCharCode(num + 63);
  console.log(num_row);
  td[0].textContent = num_row;
  for (var i = 1; i < td.length; ++i) {
    var input;
    if (i != td.length - 1) {
      input = td[i].querySelectorAll("input")[0];
    } else {
      input = td[i].querySelectorAll("select")[0];
    }
    console.log(input);
    console.log(input.name);
    console.log(input.id);
    input.id = input.id + num_row;
    input.name = input.name + num_row;
    console.log(input.id);
    console.log(input.name);
  }

  //var head = document.getElementsByTagName("head")[0];
  var script = document.createElement("script");
  var script1 = document.createElement("script");
  var link = document.createElement("link");
  link.rel = "stylesheet";
  link.type = "text/css";
  link.href = "https://cdn.rawgit.com/harvesthq/chosen/gh-pages/chosen.min.css";
  script.src =
    "https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js";
  script.async = true;
  script1.src =
    "https://cdn.rawgit.com/harvesthq/chosen/gh-pages/chosen.jquery.min.js";
  script1.async = true;
  link.async = true;

  //td[0].textContent = String.fromCharCode(64 + num_row);

  $(new_problems).find("tbody").append(clone);
  eval(script);
  eval(script1);
  eval(link);

  var x = document.getElementById("tags" + num_row);
  x.parentNode.insertBefore(script, x);
  x.parentNode.insertBefore(script1, x);
  x.parentNode.insertBefore(link, x);
  console.log(x);
  /*console.log("tags" + num_row);*/
  /*x.appendChild(script);*/
  /*x.appendChild(script1);*/
  /*x.appendChild(link);*/
}

function remove_problem() {
  var num = document.getElementsByTagName("tr").length;
  var num_row = String.fromCharCode(num + 65);
  console.log(num_row);
  if (num_row != "A") {
    var characterToNumber = num_row.charCodeAt(0);
    console.log(characterToNumber);
    characterToNumber -= 1;
    sessionStorage.setItem("num_row", String.fromCharCode(characterToNumber));
    var x = document.getElementsByTagName("tr");
    x[x.length - 1].remove();
  }
}

// Code taken from https://stackoverflow.com/questions/1090948/change-url-parameters-and-specify-defaults-using-javascript
function toggle_sort(url, param) {
  var newAdditionalURL = "";
  var tempArray = url.split("?");
  var baseURL = tempArray[0];
  var additionalURL = tempArray[1];
  var temp = "";
  var done = 0;
  var new_add = "";
  if (additionalURL) {
    tempArray = additionalURL.split("&");
    for (var i = 0; i < tempArray.length; i++) {
      if (tempArray[i].split("=")[0] != param) {
        newAdditionalURL += temp + tempArray[i];
        temp = "&";
      } else {
        done = 1;
        if (tempArray[i].split("=")[1] == "ASC") {
          newAdditionalURL += temp + param + "=DESC";
          baseURL = "---";
        } else {
          newAdditionalURL += temp + param + "=ASC";
          baseURL = "---";
        }
      }
    }
  }

  console.log(url);
  console.log(done);

  if (done == 0) {
    newAdditionalURL += temp + param + "=ASC";
  }

  return baseURL + "?" + newAdditionalURL;
}

function toggle_sort_handle(url) {
  new_url = toggle_sort(url, "ratsort");

  window.location.href = new_url;
}
