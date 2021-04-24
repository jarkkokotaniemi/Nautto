//"use strict";

/*

    Utils

*/

API_URI = "";

function notifyError(jqxhr) {
  let msg = jqxhr.responseJSON["@error"]["@message"];
  $("div.notification")(`<marquee scrolldelay="60" class="error"> ${msg} </marquee>`);
  $("div.notification").css("display", "block");
  setTimeout(() => {
    $("div.notification").empty();
    $("div.notification").css("display", "none");
  }, 10000);
}

function notifySuccess(body) {
  let msg = "Success!";
  if (body != null && body.name) {
    msg = `${body.name} succesfully created!`;
  }
  $("div.notification").html(`<marquee scrolldelay="60" class="success"> ${msg} </marquee>`);
  $("div.notification").css("display", "block");
  setTimeout(() => {
    $("div.notification").empty();
    $("div.notification").css("display", "none");
  }, 10000);
}

function getResource(href, renderFunction) {
  $.ajax({
    url: href,
    success: renderFunction,
    error: notifyError,
  });
}

function sendData(href, method, item, postProcessor) {
  $.ajax({
    url: href,
    type: method,
    data: JSON.stringify(item),
    contentType: "application/json",
    processData: false,
    success: postProcessor,
    error: notifyError,
  });
}

function followLink(event, a, renderer) {
  event.preventDefault();
  getResource($(a).attr("href"), renderer);
}

/*

    User

*/

function userRow(item) {
  return (
    "<tr>" +
    "<td>" +
    item.id +
    "</td>" +
    "<td>" +
    item.name +
    "</td>" +
    "<td>" +
    `<a href="${item["@controls"].self.href}" onClick="followLink(event, this, renderUser)">show</a>` +
    "</td>" +
    "</tr>"
  );
}

function deleteUser(event, a) {
  event.preventDefault();
  sendData(a.pathname, "DELETE", null, () =>
    getResource(`${API_URI}/api/users/`, renderUsers)
  );
}

function renderUser(body) {
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  renderUserForm(body["@controls"].edit);
  $("input[name='name']").val(body.name);
  $("input[name='description']").val(body.description);
  $("form label[name='submit']").before(
    "<label>Id</label>" +
      "<input type='text' name='Id' value='" +
      body.id +
      "' readonly>"
  );
  $("div.navigation").html(
    `<a href="${body["@controls"].collection.href}" onClick="followLink(event, this, renderUsers)">Collection</a>` +
      `<a href="${body["@controls"]["nautto:delete"].href}" onClick="deleteUser(event, this)">Delete</a>` +
      `<a href="${body["@controls"]["nautto:widgets-by"].href}" onClick="followLink(event, this, renderWidgets)">Widgets</a>` +
      `<a href="${body["@controls"]["nautto:layouts-by"].href}" onClick="followLink(event, this, renderLayouts)">Layouts</a>` +
      `<a href="${body["@controls"]["nautto:sets-by"].href}" onClick="followLink(event, this, renderSets)">Sets</a>`
  );
}

function renderUserForm(ctrl) {
  let form = $("<form>");
  let name = ctrl.schema.properties.name;
  let description = ctrl.schema.properties.description;
  form.attr("action", ctrl.href);
  form.attr("method", ctrl.method);
  form.submit(submitUser);
  form.append("<label>" + name.description + "</label>");
  form.append("<input type='text' name='name'>");
  form.append("<label>" + description.description + "</label>");
  form.append("<input type='text' name='description'>");
  ctrl.schema.required.forEach(function (property) {
    $("input[name='" + property + "']").attr("required", true);
  });
  form.append("<label name='submit'></label>");
  form.append("<input type='submit' name='submit' value='Submit'>");
  $("div.form").html(form);
}

function submitUser(event) {
  event.preventDefault();
  let data = {};
  let form = $("div.form form");
  data.name = $("input[name='name']").val();
  data.description = $("input[name='description']").val();
  sendData(form.attr("action"), form.attr("method"), data, getSubmittedUser);
}

function appendUserRow(body) {
  $(".resulttable tbody").append(userRow(body));
}

function getSubmittedUser(data, status, jqxhr) {
  let href = jqxhr.getResponseHeader("Location");
  if (status === "nocontent" && jqxhr.status >= 200 && jqxhr.status < 300) {
    return notifySuccess();
  }
  if (href) {
    return getResource(href, notifySuccess);
  }
}

function renderAddUser(body) {
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  renderUserForm(body["@controls"]["nautto:add-user"]);
  $("div.navigation").html(
    `<a href="${body["@controls"].self.href}" onClick="followLink(event, this, renderUsers)">Collection</a>`
  );
}

function renderUsers(body) {
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  $(".resulttable thead").html(
    "<tr><th>Id</th><th>Name</th><th>Actions</th></tr>"
  );
  let tbody = $(".resulttable tbody");
  body.items.forEach(function (item) {
    tbody.append(userRow(item));
  });
  $("div.form").empty();
  $("div.navigation").html(
    `<a href="${body["@controls"].self.href}" onClick="followLink(event, this, renderAddUser)">Add user</a>`
  );
}

/*

    Entrypoint
    
*/

$(document).ready(function () {
  getResource(`${API_URI}/api/users/`, renderUsers);
});
