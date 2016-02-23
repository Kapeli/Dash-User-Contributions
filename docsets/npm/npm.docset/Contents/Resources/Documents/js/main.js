/* globals $ */

$(function () {
  $('nav h2 a').on('click', function (e) {
    $(this).closest('section').toggleClass('active')
    return false
  })

  $.getJSON('https://semver.io/npm.json')
    .done(function (versions, textStatus, xhr) {
      if (versions && versions.stable) {
        $('#npm-stable-version').text(versions.stable)
        $('#npm-stable-version').attr('href', 'https://github.com/npm/npm/releases/tag/v' + versions.stable)
        $('#npm-install-instructions').show()
      }
    })
})
