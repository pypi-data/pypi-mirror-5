$(document).ready(function(){

	$('.movie').each(function(i, obj) {
    	
    	var movie_title = $(obj).find('.movie-title').text();
	
		$.ajax({
	  		url: "https://gdata.youtube.com/feeds/api/videos?q=" + encodeURIComponent(movie_title) + "&start-index=1&max-results=1&v=2&alt=json&hd&format=5",
	  		context: obj
		}).done(function(data) {
  		
  			var movie_id = data.feed.entry[0].media$group.yt$videoid.$t;
  			$(this).find('.movie-trailer').append('<iframe title="YouTube video player" class="youtube-player" type="text/html" width="640" height="390" src="https://www.youtube.com/embed/' + movie_id + '" frameborder="0" allowFullScreen></iframe>');
		});
	});
	
});	