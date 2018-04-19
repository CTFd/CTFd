window.challenge.renderer = new markdownit({
    html: true,
});

window.challenge.preRender = function(){

};

window.challenge.render = function(markdown){
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function(){

};