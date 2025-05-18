var isMobile = true;
$(document).ready(function(){

	// isMobile check
	if($('.hidden-xs').css('display')=="none"){isMobile = true;} 
	else {isMobile = false;}

	// all event height
	if(isMobile==false){
		$('.height_auto').each(function(){
			$(this).removeClass('height_auto');
		});
		$('.all_events').height($('.calc_event_all_height').height()-30);
		$('.smooth_scroll').each(function(){
			$(this).niceScroll({cursorborder:""}); 
		});
	}
	else{
		$('.smooth_scroll').each(function(){
			$(this).addClass('height_auto');
			$(this).getNiceScroll().remove();
		});
	}
	
	// width of resorce slider in navigation
	var resource_slider_item = 0;
	$('.resource_slider .item').each(function(){
		resource_slider_item++;
	});
	$('.resouce_slider_container').width(resource_slider_item*180);


	// small navigation for small devices
	$('.mnav_small > li > a').click(function(){
		$('.clicked_nav_temp ul').slideToggle();
		if(!$(this).parent().hasClass('clicked_nav_temp')){
			$('.clicked_nav_temp').removeClass('clicked_nav_temp');
			$(this).parent().addClass('clicked_nav_temp');
			$('.clicked_nav_temp ul').slideToggle();
		}
		else{
			$('.clicked_nav_temp').removeClass('clicked_nav_temp');
		}
	});

	$('.mini_nav_small').click(function(){
		$('#mini_nav_small').slideToggle();
	});

	// marqueree notice
	$('.urgent_notice').marquee({
	    duration: 15000,
	    gap: 50,
	    delayBeforeStart: 0,
	    direction: 'left',
	    duplicated: true,
	    pauseOnHover: true
	});

	// owl carousel
    $('.owl_carousel_story').owlCarousel({
        loop:true,
        responsiveClass:true,
        nav:true,
        autoplay:true,
         autoHeight : true,
        navText:['<i class="fa fa-chevron-left"></i>','<i class="fa fa-chevron-right"></i>'],
        responsive:{0    :{items:1}, 320    :{items:2}, 480    :{items:2}, 540    :{items:2}, 600    :{items:3}, 768    :{items:4}, 960    :{items:4}, 1024:{items:5}, 1280:{items:6} }
    });
    
	// owl carousel
	$('.owl_carousel_clubs').owlCarousel({
		loop:true,
		responsiveClass:true,
		nav:true,
		autoplay:true,
		navText:['<i class="fa fa-chevron-left"></i>','<i class="fa fa-chevron-right"></i>'],
		responsive:{0	:{items:1}, 320	:{items:3}, 480	:{items:4}, 540	:{items:5}, 600	:{items:6}, 768	:{items:5}, 960	:{items:5}, 1024:{items:6}, 1280:{items:7} }
	});

	// responsive slider in index html
	
	if($('#owl-demo-8').length){		
		$("#owl-demo-8").owlCarousel({
			items : 4, //10 items above 1000px browser width
			itemsDesktop : [1000,3], //5 items between 1000px and 901px
			itemsDesktopSmall : [900,3], // betweem 900px and 601px
			itemsTablet: [600,1], //2 items between 600 and 0
			itemsMobile : false, // itemsMobile disabled - inherit from itemsTablet option
			navigation : true
		});
	}
});

$(window).resize(function(){
	// isMobile check
	if($('.hidden-xs').css('display')=="none"){isMobile = true;} 
	else {isMobile = false;}
	
	// all event height
	if(isMobile==false){
		$('.height_auto').each(function(){
			$(this).removeClass('height_auto');
		});
		$('.all_events').height($('.calc_event_all_height').height()-30);
		$('.smooth_scroll').each(function(){
			$(this).niceScroll({cursorborder:""}); 
		});
	}
	else{
		$('.smooth_scroll').each(function(){
			$(this).addClass('height_auto');
			$(this).getNiceScroll().remove();
		});
	}

	// slider responsiveness
	$('.slider-container').height((407/1366)*$('body').width());
});