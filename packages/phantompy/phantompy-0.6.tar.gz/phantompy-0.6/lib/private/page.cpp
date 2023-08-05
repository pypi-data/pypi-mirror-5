#include "page.hpp"
#include "context.hpp"
#include "cookiejar.hpp"

namespace ph {

Page::Page(QObject *parent):QObject(parent), m_networkManager(this) {
    m_page.setNetworkAccessManager(&m_networkManager);
    m_page.setLinkDelegationPolicy(QWebPage::DontDelegateLinks);
    m_nmProxy.setNetworkAccessManager(&m_networkManager);

    applySettings();

#ifdef PHANTOMPY_QT4
    connect(&m_networkManager, SIGNAL(replyReceived(const QVariantMap &)),
            this, SLOT(replyReceived(const QVariantMap &)));

    connect(&m_page, SIGNAL(loadFinished(bool)),
            this, SLOT(loadFinished(bool)));

    connect(&m_page, SIGNAL(linkClicked(const QUrl &)),
            this, SLOT(linkClicked(const QUrl &)));
#else
    connect(&m_networkManager, &NetworkManager::replyReceived, this, &Page::replyReceived);
    connect(&m_page, &QWebPage::loadFinished, this, &Page::loadFinished);
    connect(&m_page, &QWebPage::linkClicked, this, &Page::linkClicked);
#endif

    m_loaded = false;
    m_error = false;
}

Page::~Page() {}

void Page::applySettings() {
    Context *ctx = Context::instance();

    m_page.settings()->setAttribute(QWebSettings::AutoLoadImages, ctx->settingsLoadImagesEnabled());
    m_page.settings()->setAttribute(QWebSettings::DnsPrefetchEnabled, ctx->settingsDnsPrefetchEnabled());
    m_page.settings()->setAttribute(QWebSettings::JavascriptEnabled, ctx->settingsJavascriptEnabled());
    m_page.settings()->setAttribute(QWebSettings::PluginsEnabled, ctx->settingsPluginsEnabled());
    m_page.settings()->setAttribute(QWebSettings::PrivateBrowsingEnabled, ctx->settingsPrivateBrowsingEnabled());
    m_page.settings()->setAttribute(QWebSettings::FrameFlatteningEnabled, ctx->settingsFrameFlatteningEnabled());
    m_page.settings()->setAttribute(QWebSettings::LocalStorageEnabled, ctx->settingsLocalStorageEnabled());
    m_page.settings()->setAttribute(QWebSettings::OfflineWebApplicationCacheEnabled, ctx->settingsOfflineApplicationCacheEnabled());
    m_page.settings()->setAttribute(QWebSettings::OfflineStorageDatabaseEnabled, ctx->settingsOfflineStorageDatabaseEnabled());

    // TODO: expose these settings to ctypes api
    m_page.settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, false);
    m_page.settings()->setAttribute(QWebSettings::JavascriptCanCloseWindows, false);
    m_page.settings()->setAttribute(QWebSettings::JavascriptCanAccessClipboard, false);
    m_page.settings()->setAttribute(QWebSettings::SiteSpecificQuirksEnabled, true);
    m_page.settings()->setAttribute(QWebSettings::LocalContentCanAccessRemoteUrls, true);
    m_page.settings()->setAttribute(QWebSettings::LocalContentCanAccessFileUrls, true);
}

void Page::load(const QString &_url) {
    m_mainUrl = QUrl::fromUserInput(_url);

    m_page.mainFrame()->load(m_mainUrl);
    m_page.mainFrame()->setScrollBarPolicy(Qt::Vertical, Qt::ScrollBarAlwaysOff);
    m_page.mainFrame()->setScrollBarPolicy(Qt::Horizontal, Qt::ScrollBarAlwaysOff);
    m_page.setViewportSize(m_viewSize);

    m_eventLoop.exec();
}

void Page::setViewSize(int x, int y) {
    this->m_viewSize = QSize(x, y);
}


bool Page::isLoaded() {
    return m_loaded;
}

bool Page::hasLoadErrors() {
    return m_error;
}

QWebFrame* Page::mainFrame() {
    return m_page.mainFrame();
}

QVariantList Page::getCookies() {
    return CookieJar::instance()->getCookies(m_page.mainFrame()->url().toString());
}

QSet<QString> Page::requestedUrls() {
    return m_requestedUrls;
}

QVariantMap Page::getResponseByUrl(const QString &url) {
    return m_responsesCache[url];
}


void Page::setInitialCookies(const QVariantList &cookies) {
    m_initialCookies = cookies;
}

QWebHistory* Page::history() {
    return m_page.history();
}

/* Private Slots */

void Page::loadFinished(bool ok) {
    m_eventLoop.quit();
    m_error = ok;
}

void Page::replyReceived(const QVariantMap &reply) {

    m_requestedUrls.insert(reply["url"].toString());
    m_responsesCache.insert(reply["url"].toString(), reply);
}

void Page::linkClicked(const QUrl &url) {
    qDebug() << "LINK CLICKED" << url.toString();
}

}

