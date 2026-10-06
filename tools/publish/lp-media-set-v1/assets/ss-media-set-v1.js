/* ss-media-set v1：YouTubeは押されるまでサムネ画像だけ（表示を軽くする）。押したら youtube-nocookie で再生 */
(function(){
  function on(btn){
    var id=btn.getAttribute('data-yt'); if(!id||btn.classList.contains('is-on'))return;
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0';
    f.title=btn.getAttribute('aria-label')||'YouTube';
    f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen=true; btn.appendChild(f); btn.classList.add('is-on');
    if(window.gtag){gtag('event','video_play',{video_id:id,page_path:location.pathname,cta_position:'media_set'});}
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.ssm-yt'); if(b){e.preventDefault();on(b);return;}
    var d=e.target.closest&&e.target.closest('[data-ssm-doc]');
    if(d&&window.gtag){gtag('event','cta_click',{cta_type:'doc_download',doc_id:d.getAttribute('data-ssm-doc'),page_path:location.pathname});}
  });
})();
