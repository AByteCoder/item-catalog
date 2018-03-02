function createCategory(){
  var name = escapeHtml($('#category-name').val().trim())
  var desc = escapeHtml($('#category-description').val().trim())
  var data = {name:name, description:desc}
  if( name == "" || desc == "")
  {
    alert("Please fill the form")
    return
  }
  $.ajax({
    type : 'POST',
    url : '/api/v1/addCategory',
    data : JSON.stringify(data),
    dataType:'json',
    contentType: 'application/json',
    success : function(result){
      var dialogId = '#'+$('#show-add').attr('data-show')
      $(dialogId).hide()
      var nl = $('#nav-list')
      var newItem = '<li><a href="/categories/'+result.id+'">'+name+'</a></li>'
      nl.html(nl.html()+newItem)
    },
    error: function(xhr,err){
      var dialogId = '#'+$('#show-add').attr('data-show')
      $(dialogId).hide()
      alert('Category creation Failed')
    }
  })
  return false
}
function createItem(){
  var name = escapeHtml($('#item-name').val())
  var desc = escapeHtml($('#item-description').val())
  var categoryId = $('#category-container').attr('data-id')
  var data = {name:name, description:desc, cid:categoryId}
  if( name == "" || desc == "")
  {
    alert("Please fill the form")
    return
  }
  $.ajax({
    type : 'POST',
    url : '/api/v1/addItem',
    data : JSON.stringify(data),
    dataType:'json',
    contentType: 'application/json',
    success : function(result){
      var dialogId = '#'+$('#show-add').attr('data-show')
      $(dialogId).hide()
      var itemContainer = $('#item-container')
      var tableHeader = '<h4>Items in {{ category.name }}</h4>\
      <div style="max-width:100%;overflow-x:auto;">\
      <table id="data-table">\
      <tr>\
      <th> Item Name </th>\
      <th> Last Updated On </th>\
      <th> Created By </th>\
      </tr>'
      if (itemContainer.attr('data-count') == 0){
        itemContainer.html(tableHeader+'</table></div>')
      }
      var table = $('#data-table')
      console.log(table +" Works")
      var newRow = '<tr>\
      <td><a href="/items/'+ result.id +'">' + name + '</a></td>\
      <td>'+calculateRelativeUserTime(new Date()).msg+'</td>\
      <td>\
      <a href="/users/'+ itemContainer.attr('data-id') + '">' +itemContainer.attr('data-name')+'</a>\
      </td>\
      </tr>'
      table.html(table.html() + newRow )
      itemContainer.attr('data-count',itemContainer.attr('data-count')+1)
      $('#item-name').val("")
      $('#item-description').val("")
    },
    error: function(xhr,err){
      var dialogId = '#'+$('#show-add').attr('data-show')
      $(dialogId).hide()
      alert('Item creation Failed')
    }
  })
  return false
}
$('#update-button').click(function(){
  $('#add-c-dialog').show()
  $('#add-close').click(function(){
    $('#add-c-dialog').hide()
  })
})
$('#update-c-button').click(function(){
  $('#update-c-dialog').show()
  $('#add-c-close').click(function(){
    $('#update-c-dialog').hide()
  })
})

$('#delete-button').click(function(){
  var id = document.getElementById("item-id").value
  var did = $(this).attr('data-id')
  $.ajax({
    type : 'DELETE',
    url : '/api/v1/items/'+id+'/',
    data : '',
    success : function(result){
      window.location.href = "/categories/"+did
    },
    error: function(xhr,err){
      alert('Item deletion Failed')
    }
  })
})
$('#delete-c-button').click(function(){
  var id = document.getElementById("category-id").value
  $.ajax({
    type : 'DELETE',
    url : '/api/v1/categories/'+id+'/',
    data : '',
    success : function(result){
      window.location.href = "/"
    },
    error: function(xhr,err){
      alert('Categorydeletion Failed')
    }
  })
})
$('#logout-button').click(function(e){
    if(provider == 1){
      e.preventDefault()
      FB.logout(function(response) {
  location.href = "/logout"
  });
    }
})

function updateItem(){
  var name = escapeHtml($('#item-name').val())
  var desc = escapeHtml($('#item-description').val())
  var id = document.getElementById("item-id").value
  var data = {name:name, description:desc}
  if( name == "" || desc == "")
  {
    alert("Please fill the form")
    return
  }
  $.ajax({
    type : 'PUT',
    url : '/api/v1/items/'+id+'/',
    data : JSON.stringify(data),
    dataType:'json',
    contentType: 'application/json',
    success : function(result){
      $('#add-c-dialog').hide()
      var converter = new showdown.Converter(),
      html = converter.makeHtml(desc);
      $('#item-n').text(name)
      $('#item-d').html(html)
    },
    error: function(xhr,err){
      $('#add-c-dialog').hide()
      alert('Item creation Failed')
    }
  })
  return false
}
$('#show-add').click(function(){
  var dialogId = '#'+$(this).attr('data-show')
  $(dialogId).show()
  $('#add-close').click(function(){
    $(dialogId).hide()
  })
})
function previewClick(){
  var containerId = $(this).attr('data-container')
  var titleId = $(this).attr('data-title')
  var descId = $(this).attr('data-desc')
  var title = escapeHtml($('#' + titleId).val().trim())
  var desc = escapeHtml($('#' + descId).val().trim())
  if( title == "")
    $('#' + titleId).css('border','1px solid red')
  else {
      $('#' + titleId).css('border','none')
      $('#' + titleId).css('border-bottom','1px solid #111')
  }

  if( desc == "")
      $('#' + descId).css('border','1px solid red')
  else
    $('#' + descId).css('border','1px solid #111')
  if( desc == "" || title == "")
  {
    alert("Please fill the form")
    return
  }
  var container = $('#' + containerId)
  var backup = container.html()
  var converter = new showdown.Converter(),
  html = converter.makeHtml(desc);
  container.html('<div id="back">\
  <img src="/static/assets/back.png" /> Back</div>\
   <h2 id="preview-title">' + title+ '</h2><hr/><p>'+ html +' </p>')
  $("#back").click(function(){
    container.html(backup)
    $('#' + titleId).val(title)
    $('#' + descId).val(desc)
    $('#preview-button').click(previewClick)
    var dialogId = '#'+$('#show-add').attr('data-show')
    $('#add-close').click(function(){
      $(dialogId).hide()
    })
  })
}
function previewClick2(){
  var containerId = $(this).attr('data-container')
  var titleId = $(this).attr('data-title')
  var descId = $(this).attr('data-desc')
  var title = escapeHtml($('#' + titleId).val().trim())
  var desc = escapeHtml($('#' + descId).val().trim())
  if( title == "")
    $('#' + titleId).css('border','1px solid red')
  else {
      $('#' + titleId).css('border','none')
      $('#' + titleId).css('border-bottom','1px solid #111')
  }

  if( desc == "")
      $('#' + descId).css('border','1px solid red')
  else
    $('#' + descId).css('border','1px solid #111')
  if( desc == "" || title == "")
  {
    alert("Please fill the form")
    return
  }
  var container = $('#' + containerId)
  var backup = container.html()
  var converter = new showdown.Converter(),
  html = converter.makeHtml(desc);
  container.html('<div id="back">\
  <img src="/static/assets/back.png" /> Back</div>\
   <h2 id="preview-title">' + title+ '</h2><hr/><p>'+ html +' </p>')
  $("#back").click(function(){
    container.html(backup)
    $('#' + titleId).val(title)
    $('#' + descId).val(desc)
    $('#preview-cbutton').click(previewClick)
    var dialogId = '#'+$('#update-c-button').attr('data-container')
    $('#add-cclose').click(function(){
      $(dialogId).hide()
    })
  })
}
$('#add-cclose').click(function(){
  $('#update-c-dialog').hide()
})
function updateCategory(){
  var name = escapeHtml($('#category-name').val())
  var desc = escapeHtml($('#category-description').val())
  var categoryId = $('#category-id').val()
  var data = {name:name, description:desc}
  if( name == "" || desc == "")
  {
    alert("Please fill the form")
    return
  }
  $.ajax({
    type : 'PUT',
    url : '/api/v1/categories/'+categoryId+'/',
    data : JSON.stringify(data),
    dataType:'json',
    contentType: 'application/json',
    success : function(result){
      $('#update-c-dialog').hide()
      var converter = new showdown.Converter(),
      html = converter.makeHtml(desc);
      $('#c-name').text(name)
      $('#c-desc').html(html)
    },
    error: function(xhr,err){
      console.log(err)
      $('#update-c-dialog').hide()
      alert('category update failed')
    }
  })
  return false
}

var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
};

function escapeHtml (string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s];
  });
}
function calculateRelativeUserTime(d)
{
  if( Math.abs(d.getTime() - Date.now()) >= 10)
  d.setTime(d.getTime() - d.getTimezoneOffset()*60*1000)
  // note d is in mysqy dtime format i.e year-month-day hour:min:sec
  var md = new Date(d)
  var nd = new Date()
  var inMs = Math.abs(nd - md)
  var inSecs = parseInt(inMs/1000)
  var adays = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
  var amonths = ['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
  if(nd.getTime() > md.getTime())
  {
    if(inSecs < 60)
    {
      return ({unit:'m',msg:'a few moments ago'})
    }else{
      var inMinutes = parseInt(inSecs/60)
      if(inMinutes < 60)
      {
        var nextTime = 60 - (inSecs - inMinutes * 60);
        return ({unit:'m',msg:inMinutes+' mins ago',next:nextTime*1000})
      }else{
        var inHours = parseInt(inMinutes/60)
        if( md.getFullYear() === nd.getFullYear() && md.getMonth() === nd.getMonth() && md.getDate() === nd.getDate())
        {
          // today
          var nextTime = 60*60 - (inSecs - inHours * 60 * 60);
          if(inHours === 1)
          return ({unit:'h',msg:inHours+' hour ago',next:nextTime*1000})
          else return ({unit:'h',msg:inHours+' hours ago',next:nextTime*1000})
        }else if(md.getFullYear() === nd.getFullYear() && md.getMonth() === nd.getMonth())
        {
          var days = nd.getDate() - md.getDate()
          if( days < 7)
          {
            if(days === 1)
            return ({unit:'n',msg:"yesterday"})
            else return ({unit:'n',msg:adays[md.getDay()]})
          }else{
            return ({unit:'n',msg:adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]})
          }
        }else if(md.getFullYear() === nd.getFullYear())
        {
          return ({unit:'n',msg:adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]})
        }else {
          return ({unit:'n',msg:adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]+", "+md.getFullYear()})
        }
      }
    }
  }else{
    var hours = md.getHours()+""
    var minutes = md.getMinutes()+""
    if(hours.length === 1)
    hours = "0"+hours
    if(minutes.length === 1)
    minutes = "0"+minutes
    var timeString = " at "+hours+":"+minutes
    if(inSecs < 60)
    {
      return ({unit:'m',msg:'in a few moments'})
    }else{
      var inMinutes = parseInt(inSecs/60)
      if(inMinutes < 60)
      {
        var nextTime = 60 - (inSecs - inMinutes * 60);
        return ({unit:'m',msg:inMinutes+' mins to go',next:nextTime*1000})
      }else{
        var inHours = parseInt(inMinutes/60)
        if( md.getFullYear() === nd.getFullYear() && md.getMonth() === nd.getMonth() && md.getDate() === nd.getDate())
        {
          // today
          var nextTime = 60*60 - (inSecs - inHours * 60 * 60);
          if(inHours === 1)
          return ({unit:'h',msg:inHours+' hour to go',next:nextTime*1000})
          else return ({unit:'h',msg:inHours+' hours to go',next:nextTime*1000})
        }else if(md.getFullYear() === nd.getFullYear() && md.getMonth() === nd.getMonth())
        {
          var days = md.getDate() - nd.getDate()
          if( days < 7)
          {
            if(days === 1)
            return ({unit:'n',msg:"tomorrow"+timeString})
            else return ({unit:'n',msg:"next "+adays[md.getDay()]+timeString})
          }else{
            return ({unit:'n',msg:"on "+adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]+timeString})
          }
        }else if(md.getFullYear() === nd.getFullYear())
        {
          return ({unit:'n',msg:"on "+adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]+timeString})
        }else {
          return ({unit:'n',msg:"on "+adays[md.getDay()]+", "+md.getDate()+" "+amonths[md.getMonth()]+", "+md.getFullYear()+timeString})
        }
      }
    }
  }
}
$('#preview-button').click(previewClick)
$(document).ready(function(){
  $('.convert-to').each(function(){
    var date = new Date($(this).text())
    $(this).text(calculateRelativeUserTime(date).msg)
  })
})
$('#preview-c-button').click(previewClick2)
