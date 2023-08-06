$(document).ready(function(){
    $('p.goToTop').click(function(event){
        event.preventDefault();
        $('html,body').animate({scrollTop:$('[name="haut"]').offset().top}, 550);
    });
});