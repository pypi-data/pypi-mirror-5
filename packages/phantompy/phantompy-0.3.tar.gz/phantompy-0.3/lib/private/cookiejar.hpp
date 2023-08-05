#ifndef PHANTOMPY_COOKIEJAR_HPP
#define PHANTOMPY_COOKIEJAR_HPP

#include <QtCore>
#include <QtNetwork>

/*
 * Partially based on PhantomJS cookiejar.h/.cpp
*/

namespace ph {

class CookieJar: public QNetworkCookieJar {
    Q_OBJECT

private:
    CookieJar(QObject *parent=0);

public:
    static CookieJar *instance();
    virtual ~CookieJar();

    void addCookie(const QNetworkCookie &cookie, const QString &url);
    void addCookieFromMap(const QVariantMap &cookie, const QString &url);
    void addCookiesFromMapList(const QVariantList &cookies, const QString &url);

    QVariantList getCookies(const QString &url);
    QVariantList getAllCookies();
};

}


#endif
