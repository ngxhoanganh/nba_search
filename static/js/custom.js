let currentUser = null;
const BASE_URL = 'http://127.0.0.1:5000';

function showMessage(elementId, message, isError = false) {
  const element = document.getElementById(elementId);
  element.textContent = message;
  element.style.display = 'block';
  element.className = `alert alert-${isError ? 'danger' : 'success'}`;
  setTimeout(() => element.style.display = 'none', 3000);
}

function updateNav() {
  const authNav = document.getElementById('auth-nav');
  if (currentUser) {
    console.log('User logged in:', currentUser);
    authNav.innerHTML = `
      <li class="nav-item">
        <span class="nav-link">Xin chào, ${currentUser.name}!</span>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#" onclick="logout()">Đăng xuất</a>
      </li>
    `;
    const newPostBtn = document.getElementById('new-post-btn');
    if (newPostBtn) {
      newPostBtn.style.display = 'inline-block';
      console.log('Showing new post button');
    }
    const commentFormContainer = document.getElementById('comment-form');
    if (commentFormContainer) {
      console.log('Showing comment form container');
      commentFormContainer.classList.add('show');
    } else {
      console.log('Comment form container not found');
    }
  } else {
    console.log('No user logged in');
    authNav.innerHTML = `
      <li class="nav-item">
        <a class="nav-link" href="/login">Đăng nhập</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/register">Đăng ký</a>
      </li>
    `;
    const commentFormContainer = document.getElementById('comment-form');
    if (commentFormContainer) {
      console.log('Hiding comment form container');
      commentFormContainer.classList.remove('show');
    }
  }
}

window.addEventListener('load', () => {
  currentUser = JSON.parse(localStorage.getItem('user'));
  console.log('Initial currentUser:', currentUser);
  updateNav();
  if (location.pathname.includes('blog')) {
    loadPosts();
  } else if (location.pathname.includes('post_detail')) {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('post_id');
    if (postId) loadPostDetail(postId);
  }
});

document.getElementById('register-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const email = document.getElementById('email').value;
  const name = document.getElementById('name').value;

  try {
    const response = await fetch(`${BASE_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, email, name })
    });
    const data = await response.json();
    showMessage('register-message', data.message, data.status === 'danger');
    if (data.status === 'success') {
      setTimeout(() => location.href = '/login', 1000);
    }
  } catch (error) {
    showMessage('register-message', 'Lỗi kết nối server!', true);
  }
});

document.getElementById('login-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    showMessage('login-message', data.message, data.status === 'danger');
    if (data.status === 'success') {
      currentUser = data.user;
      localStorage.setItem('user', JSON.stringify(currentUser));
      updateNav();
      setTimeout(() => location.href = '/blog', 1000);
    }
  } catch (error) {
    showMessage('login-message', 'Lỗi kết nối server!', true);
  }
});

function logout() {
  localStorage.removeItem('user');
  currentUser = null;
  updateNav();
  location.href = '/';
}

document.getElementById('create-post-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('title').value;
  const content = document.getElementById('content').value;
  const fileInput = document.getElementById('file');
  const formData = new FormData();
  const data = {
    userId: currentUser.id,
    title,
    content
  };
  formData.append('data', JSON.stringify(data));
  if (fileInput.files.length > 0) {
    formData.append('file', fileInput.files[0]);
  }

  try {
    const response = await fetch(`${BASE_URL}/createpost`, {
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    showMessage('post-message', result.message, result.status === 'danger');
    if (result.status === 'success') {
      setTimeout(() => location.href = '/blog', 1000);
    }
  } catch (error) {
    showMessage('post-message', 'Lỗi kết nối server!', true);
  }
});

// Xử lý form bình luận (gộp và tối ưu)
const commentForm = document.getElementById('create-comment-form');
if (commentForm) {
  // Xóa sự kiện submit cũ (nếu có)
  commentForm.replaceWith(commentForm.cloneNode(true));
  const newCommentForm = document.getElementById('create-comment-form');
  newCommentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const content = document.getElementById('comment-content').value;
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('post_id');

    if (!currentUser || !currentUser.id) {
      showMessage('post-message', 'Vui lòng đăng nhập để bình luận!', true);
      return;
    }

    const submitBtn = newCommentForm.querySelector('.submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Đang gửi...';

    try {
      console.log('Submitting comment:', content); // Debug
      const response = await fetch(`${BASE_URL}/comment/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ postId: parseInt(postId), userId: currentUser.id, content })
      });
      const data = await response.json();
      showMessage('post-message', data.message, data.status === 'danger');
      if (data.status === 'success') {
        newCommentForm.reset();
        loadComments(postId);
      }
    } catch (error) {
      console.error('Lỗi đăng bình luận:', error);
      showMessage('post-message', 'Lỗi kết nối server!', true);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Gửi';
    }
  });
}

async function loadComments(postId) {
  try {
    const response = await fetch(`${BASE_URL}/comments/${postId}`);
    const data = await response.json();
    if (data.status === 'success') {
      const commentsContainer = document.getElementById('comments-container');
      commentsContainer.innerHTML = data.comments.length ? '' : '<p>Chưa có bình luận nào.</p>';
      data.comments.forEach(comment => {
        const commentElement = document.createElement('div');
        commentElement.className = 'comment';
        commentElement.innerHTML = `
          <p><strong>${comment.username}</strong>: ${comment.content}<br><small>${new Date(comment.createdAt).toLocaleString()}</small></p>
        `;
        commentsContainer.appendChild(commentElement);
      });
    } else {
      showMessage('post-message', data.message || 'Lỗi tải bình luận!', true);
    }
  } catch (error) {
    console.error('Lỗi tải bình luận:', error);
    showMessage('post-message', 'Lỗi tải bình luận. Vui lòng thử lại!', true);
  }
}

async function loadPosts() {
  try {
    const response = await fetch(`${BASE_URL}/getallposts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start: 0, limit: 10 })
    });
    const data = await response.json();
    if (data.status === 'success') {
      displayPosts(data.posts);
    } else {
      showMessage('posts-message', data.message, true);
    }
  } catch (error) {
    console.error('Error loading posts:', error);
    showMessage('posts-message', 'Lỗi tải bài viết. Vui lòng thử lại!', true);
  }
}

function displayPosts(posts) {
  const container = document.querySelector('.player_info_item') || document.getElementById('posts-container');
  container.innerHTML = posts.length ? '' : '<p class="text-white">Chưa có bài viết nào. Hãy đăng bài đầu tiên!</p>';
  posts.forEach(post => {
    const postElement = document.createElement('div');
    postElement.className = 'item post-card';
    postElement.innerHTML = `
      <h3 class="post-title">${post.title}</h3>
      <div class="post-meta">Đăng bởi ${post.username} vào ${new Date(post.createdAt).toLocaleString()}</div>
      ${post.imageUrl ? `<img src="${post.imageUrl}" alt="Post Image" class="post-image">` : ''}
      <div class="post-content">${post.content}</div>
      <a href="/post_detail?post_id=${post.postId}" class="read-more">Xem chi tiết</a>
    `;
    container.appendChild(postElement);
  });
  if ($('.player_info_item').length) {
    $('.player_info_item').owlCarousel({
      items: 1,
      loop: true,
      dots: false,
      autoplay: true,
      margin: 40,
      autoplayHoverPause: true,
      autoplayTimeout: 5000,
      nav: true,
      navText: [
        '<img src="/static/img/icon/left.svg" alt="">',
        '<img src="/static/img/icon/right.svg" alt="">'
      ],
      responsive: {
        0: { margin: 15 },
        600: { margin: 10 },
        1000: { margin: 10 }
      }
    });
  }
}

async function loadPostDetail(postId) {
  try {
    const response = await fetch(`${BASE_URL}/getpostbyid`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ postId })
    });
    const data = await response.json();
    if (data.status === 'success') {
      displayPostDetail(data.post);
      loadComments(postId);
    } else {
      showMessage('post-message', data.message, true);
    }
  } catch (error) {
    showMessage('post-message', 'Lỗi kết nối server!', true);
  }
}

function displayPostDetail(post) {
  const container = document.getElementById('post-detail');
  container.innerHTML = `
    <h3 class="post-title">${post.title}</h3>
    <div class="post-meta">Đăng bởi ${post.username} vào ${new Date(post.createdAt).toLocaleString()}</div>
    ${post.imageUrl ? `<img src="${post.imageUrl}" alt="Post Image" class="post-image">` : ''}
    <div class="post-content">${post.content}</div>
    <p>Upvotes: <span id="upvote-count-${post.postId}">${post.upvote}</span></p>
    <button class="upvote-btn" onclick="upvotePost(${post.postId})" ${!currentUser ? 'disabled' : ''}>Upvote</button>
  `;
}

async function upvotePost(postId) {
  if (!currentUser || !currentUser.id) {
    showMessage('post-message', 'Vui lòng đăng nhập để upvote!', true);
    return;
  }
  if (!postId) {
    showMessage('post-message', 'Bài viết không hợp lệ!', true);
    return;
  }
  try {
    const response = await fetch(`${BASE_URL}/upvote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ postId, userId: currentUser.id })
    });
    const data = await response.json();
    showMessage('post-message', data.message, data.status === 'danger');
    if (data.status === 'success') {
      const upvoteCount = document.getElementById(`upvote-count-${postId}`);
      upvoteCount.textContent = parseInt(upvoteCount.textContent) + 1;
    }
  } catch (error) {
    showMessage('post-message', 'Lỗi kết nối server!', true);
  }
}

// jQuery Plugins
(function ($) {
  "use strict";
  var review = $('.player_info_item');
  if (review.length) {
    review.owlCarousel({
      items: 1,
      loop: true,
      dots: false,
      autoplay: true,
      margin: 40,
      autoplayHoverPause: true,
      autoplayTimeout: 5000,
      nav: true,
      navText: [
        '<img src="/static/img/icon/left.svg" alt="">',
        '<img src="/static/img/icon/right.svg" alt="">'
      ],
      responsive: {
        0: { margin: 15 },
        600: { margin: 10 },
        1000: { margin: 10 }
      }
    });
  }

  $('.popup-youtube, .popup-vimeo').magnificPopup({
    type: 'iframe',
    mainClass: 'mfp-fade',
    removalDelay: 160,
    preloader: false,
    fixedContentPos: false
  });

  $(window).scroll(function () {
    var window_top = $(window).scrollTop() + 1;
    if (window_top > 50) {
      $('.main_menu').addClass('menu_fixed animated fadeInDown');
    } else {
      $('.main_menu').removeClass('menu_fixed animated fadeInDown');
    }
  });

  if (document.getElementById('default-select')) {
    $('select').niceSelect();
  }

  $('.grid').masonry({
    itemSelector: '.grid-item',
    columnWidth: '.grid-sizer',
    percentPosition: true
  });

  if ($('.img-gal').length > 0) {
    $('.img-gal').magnificPopup({
      type: 'image',
      gallery: {
        enabled: true
      }
    });
  }
})(jQuery);