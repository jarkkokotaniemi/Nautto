//"use strict";

const API_URI = "";

/* 
  Pure 
*/

const itemRowMarkup = (item) => {
  const ctrls = item["@controls"]
  const link = linkMarkup(ctrls.self.href, "followLink(event, this, renderItem)", "show")
  return (`<tr><td>${item.id}</td><td>${item.name}</td><td>${link}</td></tr>`);
}

const linkMarkup = (href, onClick, text) => {
  return `<a href="${href}" onClick="${onClick}">${text}</a>`
}

const getNavigation = (ctrls) => {
  return "" +
    ((ctrls.collection != null) ? linkMarkup(ctrls.collection.href, "followLink(event, this, renderCollection)", "Collection") : "") +
    ((ctrls.up != null) ? linkMarkup(ctrls.up.href, "followLink(event, this, renderItem)", "Up") : "") +
    ((ctrls.author != null) ? linkMarkup(ctrls.author.href, "followLink(event, this, renderItem)", "Author") : "") +
    ((ctrls["nautto:delete"] != null) ? linkMarkup(ctrls["nautto:delete"].href, "deleteItem(event, this)", "Delete") : "") +
    ((ctrls["nautto:widgets-by"] != null) ? linkMarkup(ctrls["nautto:widgets-by"].href, "followLink(event, this, renderCollection)", "Widgets") : "") +
    ((ctrls["nautto:layouts-by"] != null) ? linkMarkup(ctrls["nautto:layouts-by"].href, "followLink(event, this, renderCollection)", "Layouts") : "") +
    ((ctrls["nautto:sets-by"] != null) ? linkMarkup(ctrls["nautto:sets-by"].href, "followLink(event, this, renderCollection)", "Sets") : "") +
    ((ctrls["nautto:users-all"] != null) ? linkMarkup(ctrls["nautto:users-all"].href, "followLink(event, this, renderCollection)", "All users") : "") +
    ((ctrls["nautto:widgets-all"] != null) ? linkMarkup(ctrls["nautto:widgets-all"].href, "followLink(event, this, renderCollection)", "All widgets") : "") +
    ((ctrls["nautto:layouts-all"] != null) ? linkMarkup(ctrls["nautto:layouts-all"].href, "followLink(event, this, renderCollection)", "All layouts") : "") +
    ((ctrls["nautto:sets-all"] != null) ? linkMarkup(ctrls["nautto:sets-all"].href, "followLink(event, this, renderCollection)", "All sets") : "") +
    ((ctrls["nautto:add-user"] != null) ? linkMarkup(ctrls["nautto:add-user"].href, "followLink(event, this, renderAddItem('nautto:add-user'))", "Add user") : "") +
    ((ctrls["nautto:add-widget"] != null) ? linkMarkup(ctrls["nautto:add-widget"].href, "followLink(event, this, renderAddItem('nautto:add-widget'))", "Add widget") : "") +
    ((ctrls["nautto:add-layout"] != null) ? linkMarkup(ctrls["nautto:add-layout"].href, "followLink(event, this, renderAddItem('nautto:add-layout'))", "Add layout") : "") +
    ((ctrls["nautto:add-set"] != null) ? linkMarkup(ctrls["nautto:add-set"].href, "followLink(event, this, renderAddItem('nautto:add-set'))", "Add set") : "")
}

const getPreview = (iter) => {
  if ("type" in iter && "content" in iter && iter.type === "HTML") {
    return iter.content;
  }
  return "";
}

const propertyToInput = (required) => ([key, value]) => {
  const label = value.description || key
  const requiredFlag = required.includes(key)
  return inputMarkup(label , "text", key, requiredFlag)
}

const inputMarkup = (label, type, name, required) => {
  return `<label>${label}</label><input type='${type}' name='${name}' ${(required) ? "required" : ""}>`;
}

const getItemForm = (ctrl) => {
  const schema = ctrl.schema

  const form = $("<form>");
  form.attr("action", ctrl.href);
  form.attr("method", ctrl.method);
  form.submit(submitItem);

  const withoutId = Object.entries(schema.properties).filter(([key, _]) => key !== "id")
  const inputs_n_labels = withoutId.map(propertyToInput(ctrl.schema.required))
  form.html(inputs_n_labels);
  form.append("<label name='submit'></label>");
  form.append("<input type='submit' name='submit' value='Submit'>");
  return form;
}

const getSubmittedItem = (data, status, jqxhr) => {
  let href = jqxhr.getResponseHeader("Location");
  if (status === "nocontent" && jqxhr.status >= 200 && jqxhr.status < 300) {
    return notifySuccess();
  }
  if (href) {
    return getResource(href, notifySuccess);
  }
}

/*
  Not so pure
*/

const notifyError = (jqxhr) => {
  let msg = jqxhr.responseJSON["message"];

  /* Side-effects */
  $("div.notification").html(`<marquee scrolldelay="60" class="error"> ${msg} </marquee>`);
  $("div.notification").css("display", "block");
  setTimeout(() => {
    $("div.notification").empty();
    $("div.notification").css("display", "none");
  }, 10000);
  return;
}

const notifySuccess = (body) => {
  let msg = "Success!";
  if (body != null && body.name) {
    msg = `${body.name} succesfully created!`;
  }

  /* Side-effects */
  $("div.notification").html(`<marquee scrolldelay="60" class="success"> ${msg} </marquee>`);
  $("div.notification").css("display", "block");
  setTimeout(() => {
    $("div.notification").empty();
    $("div.notification").css("display", "none");
  }, 10000);
  return;
}

const getResource = (href, renderFunction) => {
  /* Side-effects */
  $.ajax({
    url: href,
    success: renderFunction,
    error: notifyError,
  });
  return;
}

const sendData = (href, method, item, postProcessor) => {
  /* Side-effects */
  $.ajax({
    url: href,
    type: method,
    data: JSON.stringify(item),
    contentType: "application/json",
    processData: false,
    success: postProcessor,
    error: notifyError,
  });
  return;
}

const followLink = (event, a, renderer) => {
  /* Side-effects */
  event.preventDefault();
  getResource($(a).attr("href"), renderer);
  return;
}

const renderCollection = (body) => {
  const items = body.items.map(itemRowMarkup).join(" ")
  const links = getNavigation(body["@controls"])
  const preview_display = (getPreview(body)) ? "block" : "none";
  
  /* Side-effects */
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  $(".resulttable thead").html("<tr><th>Id</th><th>Name</th><th>Actions</th></tr>");
  $(".resulttable tbody").html(items)
  $("div.navigation").html(links);
  $("div.form").empty();
  $("div.preview").css("display", preview_display);
  return;
}

const renderItem = (body) => {
  const ctrls = body["@controls"];
  const filtered_body = Object.entries(body).filter(([key, _]) => !key.includes("@"))
  const preview = getPreview(body);
  const preview_display = (preview) ? "block" : "none";
  const links = getNavigation(ctrls);
  const form = getItemForm(ctrls.edit)

  /* Side-effects */
  $("div.form").html(form);
  filtered_body.forEach(([key, value]) => {$(`input[name='${key}']`).val(value);});
  $("form label[name='submit']").before(`<label>Id</label><input type='text' name='Id' value='${body.id}' readonly>`);
  $("div.navigation").html(links);
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  $("div.preview").html("preview" + preview)
  $("div.preview").css("display", preview_display);
  return;
}

const submitItem = (event) => {
  const data = {
    name: $("input[name='name']").val(),
    description: $("input[name='description']").val(),
    type: $("input[name='type']").val(),
    content: $("input[name='content']").val()
  };
  const form = $("div.form form");

  /* Side-effects */
  event.preventDefault();
  sendData(form.attr("action"), form.attr("method"), data, getSubmittedItem);
  return;
}

const deleteItem = (event, a) => {
  const splitted = a.pathname.split("/");
  const collection = splitted.slice(splitted.length - 3, splitted.length - 2)

  /* Side-effects */
  event.preventDefault();
  sendData(a.pathname, "DELETE", null, () =>
    notifySuccess(),
    getResource(`${API_URI}/api/${collection}/`, renderCollection)
  );
  return;
}

const renderAddItem = (relation) => (body) => {
  const form = getItemForm(body["@controls"][relation])

  /* Side-effects */
  $("div.form").html(form);
  $(".resulttable thead").empty();
  $(".resulttable tbody").empty();
  $("div.navigation").html(`<a href="${body["@controls"].self.href}" onClick="followLink(event, this, renderCollection)">Collection</a>`);
  return;
}

/* 
  Entrypoint 
*/

$(document).ready(() => getResource(`${API_URI}/api/users/`, renderCollection));