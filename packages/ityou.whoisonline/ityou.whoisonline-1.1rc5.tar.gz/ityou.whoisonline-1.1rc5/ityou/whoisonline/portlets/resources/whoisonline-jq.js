// =============== ANFANG ================================
$(document).ready(
    function () {
    	
    	var WHOISONLINE_DELAY =  parseInt($("#WHOISONLINE_DELAY").text())
    	var ESI_ROOT = $("#ESI_ROOT").text()
    	var ajax_whoisonline = ESI_ROOT  + '/@@whoisonline-ajax'    	
    	var whotimer = 0;
		
		function user_profile(user_id) {
			function get_userprofile() {
				$.getJSON(ajax_whoisonline , {
					'action':'show_userprofile', 
					'user_id': user_id},
					function(userprofile) {	
						if (userprofile != '') {
				            $("#userprofile-tmpl").tmpl(userprofile).appendTo($(".userprofile-box"));
						};
					});       	
			};    
		    get_userprofile();
		}
		
		function show_whoisonline_portlet(size) { 
		    // empty box: 156	
			if (    $("#who-is-online > div").length    ) {
			    if ( $("#who-is-online > div").html().length > size  ) {
			        $("#who-is-online").parent().parent().fadeIn();
			    } else {
			        $("#who-is-online").parent().parent().hide();
			    }
			}
		}
		
		function whoisonline () {
		    // ---- whoisonline -----------
		    $.ajax({
		        url: ajax_whoisonline,
		        type: 'POST',
		        dataType: 'html',     
		        timeout: 1000,
		        error: function(){
		            $("#debug").html("WhoIsOnline-DB not readable").show();
		        },
		        success: function(who_is_online_response){
		        	// 	--- xml in box anzeigen
		        	who_is_online = who_is_online_response;
		            if (who_is_online.length > 100 ) { // > 0 fails because plone sents white space !!!
		            	$(".portletWhoIsOnline").slideDown(300, function() {
		               		$("#who-is-online").html( who_is_online ).fadeIn(800)
		            	});
		            } else {
		            	$(".portletWhoIsOnline").hide();
		            };
		            
					// hoverintent ---
					var config = {    			     			
		                over: function() {
							// stop ajax requests
							
		        			var user_id = $(this).attr('id');
		        			var userprofile_box = $(this).find(".userprofile-box");        			
		        			
		        			//alert(user_id, userprofile_box.html() )
							
		                    if(whotimer) {
								clearTimeout(whotimer);
								whotimer = null
								};
								
								// erweiterung ---  						
			                    $.getJSON(ajax_whoisonline, {
					                    'action':'show_userprofile', 
					                    'user_id': user_id
					                    },
					                    function(userprofile) {	
						                    if (userprofile != '') {
				                                $("#userprofile-tmpl").tmpl(userprofile).appendTo(  userprofile_box  ).fadeIn(100);
						                    };
					                    });       	
		
								// /erweiterung -----
		                },
		                out: function() {
		        			var userprofile_box = $(this).parent().find(".userprofile-box");                
				            $(this).find(".who-is-online-box, #who-is-online .arrow-top").fadeOut(100);
		                    userprofile_box.empty();		            
		                }, 				 
		                timeout: 200, // number = milliseconds delay before onMouseOut
		                interval:200,
						sensitivity:10
					};
					$("#who-is-online").find(".portrait").hoverIntent(config);
		
		        }
		    });	        
		
		}
		// --- end notify order -------------------            


                        
        // === BEGIN ====================================
            	
    	// --- Who is online ----------
    	
  	    if ( $("#who-is-online").length > 0  ) { 
		    $("#debug3").html(whotimer);
		    
            whotimer = setInterval(function () {
                whoisonline() ;
                show_whoisonline_portlet(156);
            }, WHOISONLINE_DELAY);
            whoisonline() ;
        }      
        // --- /Who is online ---------

  	    $("#logout").click( function() {
  	    	window.location.href = "logout";
  	    });
        
  	    
        // === END ======================================
    }
); 



