/*=============== DARK LIGHT THEME ===============*/
const themeButton = document.getElementById('theme-button')
const darkTheme = 'dark-theme'
const iconTheme = 'bx-sun'

// Previously selected topic (if user selected)
const selectedTheme = localStorage.getItem('selected-theme')
const selectedIcon = localStorage.getItem('selected-icon')

// We obtain the current theme that the interface has by validating the dark-theme class
const getCurrentTheme = () => document.body.classList.contains(darkTheme) ? 'dark' : 'light'
const getCurrentIcon = () => themeButton.classList.contains(iconTheme) ? 'bx bx-moon' : 'bx bx-sun'

// We validate if the user previously chose a topic
if (selectedTheme) {
  // If the validation is fulfilled, we ask what the issue was to know if we activated or deactivated the dark
  document.body.classList[selectedTheme === 'dark' ? 'add' : 'remove'](darkTheme)
  themeButton.classList[selectedIcon === 'bx bx-moon' ? 'add' : 'remove'](iconTheme)
}

// Activate / deactivate the theme manually with the button
themeButton.addEventListener('click', () => {
    // Add or remove the dark / icon theme
    document.body.classList.toggle(darkTheme)
    themeButton.classList.toggle(iconTheme)
    // We save the theme and the current icon that the user chose
    localStorage.setItem('selected-theme', getCurrentTheme())
    localStorage.setItem('selected-icon', getCurrentIcon())
})

/*=============== CHANGE BACKGROUND HEADER ===============*/
function scrollHeader(){
    const header = document.getElementById('header')
    // When the scroll is greater than 50 viewport height, add the scroll-header class to the header tag
    if(this.scrollY >= 50) header.classList.add('scroll-header'); else header.classList.remove('scroll-header')
}
window.addEventListener('scroll', scrollHeader)

/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/*===== MENU SHOW =====*/
/* Validate if constant exists */
if(navToggle){
    navToggle.addEventListener('click', () =>{
        navMenu.classList.add('show-menu')
    })
}

/*===== MENU HIDDEN =====*/
/* Validate if constant exists */
if(navClose){
    navClose.addEventListener('click', () =>{
        navMenu.classList.remove('show-menu')
    })
}

/*=============== REMOVE MENU MOBILE ===============*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction(){
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))

function change_class_vote(type, object, data)
{
    if(data['voter'] === 1)
    {
        $(type).addClass("upvote");
        $(type).closest(object).find('[title="downvote"]').removeClass("downvote");

    }
    else if(data['voter'] === 0)
    {
        $(type).closest(object).find('[title="upvote"]').removeClass("upvote");
        $(type).closest(object).find('[title="downvote"]').removeClass("downvote");
    }
    else
    {
        $(type).addClass("downvote");
        $(type).closest(object).find('[title="upvote"]').removeClass("upvote");
    }
}
var flag = false;
function embedVideo(url) {
    if($('#embed_video').is(":hidden") && flag === false)
    {
        $.ajax({
        url: "https://www.youtube.com/oembed?url=" + url + "&format=json&maxwidth=720&maxheight=480",
        type: 'GET',
        success: function (embed_video_json) {
            $('#embed_video').html(embed_video_json.html);
            $("#embed_video").toggle();
            flag = true;
            },
            error: function() {
                console.log('failed to retrieve video');
            }
        });
    }
    else
    {

        $("#embed_video").toggle();
    }
}

$("#hide").click(function(){
    $("#form--hidden").toggle();
});

let start = async function() {
    visitorId = await biri();
}

function open_reply(form_id) {
    $("#reply" + form_id).toggleClass("show_form");
}

$(document).on("click", '.hide--comment', function() {
    let comment = $(this).parents('div');
    comment.next('.comment--content').toggle();

    if ($(this).hasClass("uil-plus-square")) {
        $(this).addClass('uil uil-minus-square-full').removeClass('uil uil-plus-square');
    }
    else {
        $(this).addClass('uil uil-plus-square').removeClass('uil uil-minus-square-full');
    }

});