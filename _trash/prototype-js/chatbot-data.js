/**
 * FAN HUB+ Assistant Knowledge Base & Onboarding Script
 * Plain data module separated from behavior engine.
 */

window.FANHUB_CHATBOT_DATA = {
  // 11 Core Knowledge Base FAQ entries
  faqs: [
    {
      id: 'about',
      keywords: ['what is fan hub', 'about', 'platform', 'what can i do', 'features', 'overview'],
      question: 'What is Fan Hub+ and what can I do here?',
      answer: 'Fan Hub+ is the ultimate entertainment universe uniting Anime simulcasts, Gaming realm hubs, Movies, K-Pop concert stages, and Manga scanlations. You can watch high-res trailers, save titles to your personal collection, join community theories, book convention passes, and shop official goodies!',
      relatedLinks: [
        { label: 'Explore Fandoms →', href: 'explore.html' },
        { label: 'Discovery Matrix →', href: 'explore.html' }
      ]
    },
    {
      id: 'auth',
      keywords: ['account', 'create account', 'register', 'sign in', 'log in', 'login', 'signup', 'membership'],
      question: 'How do I create an account or sign in?',
      answer: 'Click "Register" at the top right to start our 4-step wizard. You can configure your profile, pick your favorite fandoms, and set your theme. If you already have an account, click "Sign In" with your username or email.',
      relatedLinks: [
        { label: 'Sign In →', href: 'login.html' },
        { label: 'Create Account →', href: 'register.html' }
      ]
    },
    {
      id: 'collection',
      keywords: ['collection', 'watchlist', 'favorites', 'save', 'plan to watch', 'bookmark', 'watching'],
      question: 'What is Collection and how do I manage my watchlist?',
      answer: 'Your Collection is your personalized cloud library where you can track currently watching episodes, plan-to-watch queues, and favorite titles. When logged in, click "Resume", "Rewatch", or "Archive" on any series card.',
      relatedLinks: [
        { label: 'My Collection →', href: 'collection.html' }
      ]
    },
    {
      id: 'downloads',
      keywords: ['download', 'downloads', 'offline', 'storage', 'cache', 'play offline', 'no internet'],
      question: 'How do Downloads work and can I watch offline?',
      answer: 'The Downloads & Storage Manager allows you to cache episodes for offline playback with zero buffering. You can pause or resume active queues and use the built-in Offline Episode Player with multi-track audio.',
      relatedLinks: [
        { label: 'Downloads & Storage →', href: 'downloads.html' }
      ]
    },
    {
      id: 'community',
      keywords: ['community', 'discuss', 'forum', 'discussion', 'theories', 'upvote', 'new thread', 'reactions'],
      question: 'What is Community and how do I post discussions?',
      answer: 'Community is the discussion forum for theories, episode reactions, and fan art. Upvote interesting posts with the chevron button, or click "New Discussion" to publish your own lore breakdown to the community feed!',
      relatedLinks: [
        { label: 'Community Feed →', href: 'community.html' }
      ]
    },
    {
      id: 'search',
      keywords: ['search', 'find', 'hotkey', 'shortcut', 'slash', 'filter', 'keyboard'],
      question: 'How do I search and what does the "/" shortcut do?',
      answer: 'Pressing "/" anywhere on the keyboard immediately focuses the top global search bar. Typing instantly live-filters cards on your current page. Pressing Enter takes you to the full Multiverse Discovery Matrix!',
      relatedLinks: [
        { label: 'Discovery Matrix →', href: 'explore.html' }
      ]
    },
    {
      id: 'goodies',
      keywords: ['goodies', 'shop', 'store', 'cart', 'buy', 'price', 'checkout', 'payment', 'merch', 'figurine'],
      question: 'How does Goodies checkout work and is payment real?',
      answer: 'Goodies is our licensed collectibles store offering scale figurines, manga box sets, and cosplay gear. Click "Add to Bag" on any item to update your cart drawer. Note: Checkout generates a mock order confirmation number (#FAN-XXXXX) for demo purposes — no real payment is charged!',
      relatedLinks: [
        { label: 'Goodies Shop →', href: 'goodies.html' }
      ]
    },
    {
      id: 'theme_settings',
      keywords: ['theme', 'dark mode', 'light mode', 'font size', 'scale', 'display', 'appearance', 'settings'],
      question: 'How do I change theme or font size?',
      answer: 'Click the sun/moon icon in the header to toggle between Dark and Light mode. For deeper customizations (including Cyber Neon theme and Compact/Standard/Comfortable font scales), visit Account Settings.',
      relatedLinks: [
        { label: 'Settings →', href: 'settings.html' }
      ]
    },
    {
      id: 'events',
      keywords: ['events', 'tickets', 'convention', 'con', 'expo', 'tour', 'book pass', 'badge'],
      question: 'How do Events and ticket reservations work?',
      answer: 'The Events portal lists premier conventions like Anime Expo, Gamescom, and stadium world tours. Click "Book Pass" on any event card to open the ticket modal, select your tier (VIP or GA), and receive your unique pass code (#FH-TKT-XXXXXX).',
      relatedLinks: [
        { label: 'Events Radar →', href: 'events.html' }
      ]
    },
    {
      id: 'submissions',
      keywords: ['submit', 'creator', 'studio', 'upload', 'amv', 'clip', 'guidelines', 'views'],
      question: 'How do I submit content to Creator Studio?',
      answer: 'Creator Studio allows creators to upload AMV edits, cosplay galleries, and lore theories up to 2.5 GB. Drag and drop your file, select a category, and submit for editorial review to earn Creator XP and track analytics.',
      relatedLinks: [
        { label: 'Creator Studio →', href: 'submissions.html' }
      ]
    },
    {
      id: 'fandoms',
      keywords: ['fandoms', 'hubs', 'universes', 'portals', 'hall of fame', 'characters', 'vote'],
      question: 'What are Fandom Hubs?',
      answer: 'Fandom Hubs are dedicated universe portals categorized by Anime, Gaming, Cinema, K-Pop, and Manga. Each hub includes character popularity polls (where you can cast a +1 vote) and canonical lore timelines.',
      relatedLinks: [
        { label: 'Fandom Portals →', href: 'explore.html' }
      ]
    }
  ],

  // Category Recommendations Knowledge
  categories: {
    'anime': {
      title: 'Anime Universe',
      page: 'anime.html',
      featured: 'Demon Slayer: Swordsmith Village Arc',
      featuredWatch: 'watch.html?title=demon-slayer'
    },
    'gaming': {
      title: 'Gaming Realm',
      page: 'gaming.html',
      featured: 'Grand Theft Auto VI',
      featuredWatch: 'watch.html?title=naruto'
    },
    'movies': {
      title: 'Movies & Cinema',
      page: 'movies.html',
      featured: 'Demon Slayer: Mugen Train ($507M)',
      featuredWatch: 'watch.html?title=demon-slayer'
    },
    'kpop': {
      title: 'K-Pop Wave',
      page: 'kpop.html',
      featured: 'BLACKPINK Born Pink World Tour',
      featuredWatch: 'watch.html?title=one-piece'
    },
    'manga': {
      title: 'Manga Sanctuary',
      page: 'manga.html',
      featured: 'One Piece: Elbaph Arc Chapter 1128',
      featuredWatch: 'manga.html'
    }
  },

  // 5-Step Guided Onboarding Flow
  onboarding: [
    {
      step: 1,
      message: "Welcome to Fan Hub+! I'm your interactive fandom guide. To customize your universe, what content are you most passionate about?",
      chips: [
        { label: 'Anime', value: 'anime' },
        { label: 'Gaming', value: 'gaming' },
        { label: 'Movies', value: 'movies' },
        { label: 'K-Pop', value: 'kpop' },
        { label: 'Manga', value: 'manga' },
        { label: 'Explore All', value: 'explore' }
      ]
    },
    {
      step: 2,
      template: (cat) => `Great choice! Our ${cat.toUpperCase()} hub is packed with trending releases and lore guides. You can also press "/" anywhere to search all universes instantly, or browse the Multiverse Matrix!`,
      chips: [
        { label: 'Tell me about Watchlists', nextStep: 3 },
        { label: 'Skip to Community', nextStep: 4 }
      ]
    },
    {
      step: 3,
      message: "With a free Fan Hub+ account, your Watchlist and Downloads sync across devices. You can save episodes and even cache them for offline viewing when traveling!",
      chips: [
        { label: 'What about Community?', nextStep: 4 },
        { label: 'Take me exploring', nextStep: 5 }
      ]
    },
    {
      step: 4,
      message: "Our Community discussions let you debate theories, vote on power levels, and book passes for global conventions like Anime Expo!",
      chips: [
        { label: "Awesome, let's explore!", nextStep: 5 }
      ]
    },
    {
      step: 5,
      message: "You're all set! Feel free to ask me anything about navigation, downloads, or fandom lore at any time. Enjoy Fan Hub+!",
      chips: [
        { label: 'Explore Hub →', action: 'finish' }
      ]
    }
  ]
};
