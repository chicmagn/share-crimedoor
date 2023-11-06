$(document).ready(function () {
  $('.video-carousel').each(function(){
    if ($(window).width() > 768) {
      if ($(this).find('.gallery-cell').length > 4) {
        $(this).flickity({
          imagesLoaded: true,
          autoPlay: 5000,
          contain: true,
          cellAlign: 'left',
          wrapAround: true,
          pageDots: false,
          prevNextButtons: true,
        });
      }
    } else {
      $(this).flickity({
        imagesLoaded: true,
        autoPlay: 5000,
        contain: true,
        cellAlign: 'left',
        wrapAround: true,
        pageDots: false,
        prevNextButtons: true,
      });
    }
    
  });
  

  setTimeout(() => {
    $('#badgesModal').addClass('active');
  }, 20000);
    
  $('.modal_btn').on('click', function (e) {
    e.preventDefault();
    var id = $(this).attr('href');
    $(id).addClass('active');
  })

  $('.close').on('click', function (e) {
    e.preventDefault();
    var id = $(this).data('id');
    console.log(id);
    $(id).removeClass('active');
  });
  
  $('.menu-toggle').click(function(){
    $(".nav").toggleClass("mobile-nav");
    $(this).toggleClass("is-active");
  });

  $('.contact_questions').each(function () {
    $(this).change(function () {
      var id = $(this).val()
      console.log(id)
      $('.main').hide();
      $('.contact-form').removeClass('active');
      $(id).addClass('active');
    });
  })
  
})

$(document).on('click', function (e) {
  if ($(e.target).hasClass("modal")) {
    $("body").find(".modal").removeClass("active");
  }
});


$(document).on('scroll', function () {
  if ($(window).scrollTop() > 0) {
    $('.sticky').addClass('active');
  } else {
    $('.sticky').removeClass('active')
  }
})

// if ($('.page-content').hasClass('infinite')) {
//   var page = $('.page-content').data('page_num');

//   $(window).scroll(function() {
//       if ($(window).scrollTop() == $(document).height() - $(window).height()) {

        
//         $("body").append('<div class="big-box"><h1>Page ' + page + '</h1></div>');
//         show_loading()
//         data = {
//           "type": $('.page-content').data('type'),
//           "page": page
//         }
//         $.ajax({
//           url: '/get_page',
//           type: 'POST',
//           data: data,
//         }).done((result) => {
//             hide_loading();
//             console.log(result)
//             if (result.type == 'article') {
//               var html = '';
//               html += `<ul class="tags_list page">`;

//               for (let i = 0; i < result.data.length; i++) {
//                 const item = result.data[i];
//                 html += `<li class="grid__item one-half"> <a class="capitalize" href="/${result.type}/${item.id}">${item.title}</a></li>`
//               }
                      
//               html += `</ul>`
//             }
//         })
//       }
//   });
// }


function show_loading() {
  $(':focus').blur()
  $('.loading-section').removeClass('hide');
  // $('.main-section').css('opacity', .6);
  $('.modal').css('opacity', .6);
  let node = document.createElement("div");
  node.className += "overlay";
  document.body.appendChild(node);
};

function hide_loading() {
  let node = document.querySelector("div.overlay")
  document.body.removeChild(node);
  $('.modal').css('opacity', 1);
  $('.loading-section').addClass('hide');
  // $('.main-section').css('opacity', 1);
};