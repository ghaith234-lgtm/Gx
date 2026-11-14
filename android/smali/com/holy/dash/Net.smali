.class final Lcom/holy/dash/Net;
.super Ljava/lang/Object;
.source "Net.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/holy/dash/Net$Resp;,
        Lcom/holy/dash/Net$Progress;
    }
.end annotation


# direct methods
.method private constructor <init>()V
    .registers 1

    .prologue
    .line 19
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static download(Ljava/lang/String;Ljava/util/Map;Ljava/io/File;Lcom/holy/dash/Net$Progress;)Ljava/lang/String;
    .registers 16
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/util/Map",
            "<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;",
            "Ljava/io/File;",
            "Lcom/holy/dash/Net$Progress;",
            ")",
            "Ljava/lang/String;"
        }
    .end annotation

    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .prologue
    .line 116
    const v0, 0xea60

    invoke-static {p0, p1, v0}, Lcom/holy/dash/Net;->open(Ljava/lang/String;Ljava/util/Map;I)Ljava/net/HttpURLConnection;

    move-result-object v2

    .line 118
    :try_start_7
    invoke-virtual {v2}, Ljava/net/HttpURLConnection;->getResponseCode()I

    move-result v0

    .line 119
    const/16 v1, 0xc8

    if-eq v0, v1, :cond_2d

    new-instance v1, Ljava/io/IOException;

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "HTTP "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1
    :try_end_28
    .catchall {:try_start_7 .. :try_end_28} :catchall_28

    .line 140
    :catchall_28
    move-exception v0

    invoke-virtual {v2}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 141
    throw v0

    .line 120
    :cond_2d
    :try_start_2d
    invoke-virtual {v2}, Ljava/net/HttpURLConnection;->getContentLength()I

    move-result v0

    int-to-long v4, v0

    .line 121
    const-string v0, "SHA-256"

    invoke-static {v0}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object v3

    .line 122
    invoke-virtual {v2}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object v6

    .line 123
    new-instance v7, Ljava/io/FileOutputStream;

    invoke-direct {v7, p2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_41
    .catchall {:try_start_2d .. :try_end_41} :catchall_28

    .line 125
    const/16 v0, 0x4000

    :try_start_43
    new-array v8, v0, [B

    .line 126
    const-wide/16 v0, 0x0

    .line 128
    :cond_47
    :goto_47
    invoke-virtual {v6, v8}, Ljava/io/InputStream;->read([B)I

    move-result v9

    if-lez v9, :cond_65

    .line 129
    const/4 v10, 0x0

    invoke-virtual {v7, v8, v10, v9}, Ljava/io/OutputStream;->write([BII)V

    .line 130
    const/4 v10, 0x0

    invoke-virtual {v3, v8, v10, v9}, Ljava/security/MessageDigest;->update([BII)V

    .line 131
    int-to-long v10, v9

    add-long/2addr v0, v10

    .line 132
    if-eqz p3, :cond_47

    invoke-interface {p3, v0, v1, v4, v5}, Lcom/holy/dash/Net$Progress;->on(JJ)V
    :try_end_5c
    .catchall {:try_start_43 .. :try_end_5c} :catchall_5d

    goto :goto_47

    .line 135
    :catchall_5d
    move-exception v0

    :try_start_5e
    invoke-virtual {v7}, Ljava/io/OutputStream;->close()V

    .line 136
    invoke-virtual {v6}, Ljava/io/InputStream;->close()V

    .line 137
    throw v0

    .line 135
    :cond_65
    invoke-virtual {v7}, Ljava/io/OutputStream;->close()V

    .line 136
    invoke-virtual {v6}, Ljava/io/InputStream;->close()V

    .line 138
    invoke-virtual {v3}, Ljava/security/MessageDigest;->digest()[B

    move-result-object v0

    invoke-static {v0}, Lcom/holy/dash/Net;->hex([B)Ljava/lang/String;
    :try_end_72
    .catchall {:try_start_5e .. :try_end_72} :catchall_28

    move-result-object v0

    .line 140
    invoke-virtual {v2}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 138
    return-object v0
.end method

.method static get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;
    .registers 11
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/util/Map",
            "<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;I[",
            "Ljava/net/HttpURLConnection;",
            ")",
            "Lcom/holy/dash/Net$Resp;"
        }
    .end annotation

    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .prologue
    const/4 v6, 0x0

    const/4 v5, 0x0

    .line 66
    invoke-static {p0, p1, p2}, Lcom/holy/dash/Net;->open(Ljava/lang/String;Ljava/util/Map;I)Ljava/net/HttpURLConnection;

    move-result-object v1

    .line 67
    if-eqz p3, :cond_a

    aput-object v1, p3, v5

    .line 69
    :cond_a
    :try_start_a
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I

    move-result v2

    .line 70
    const/16 v0, 0x190

    if-lt v2, v0, :cond_27

    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getErrorStream()Ljava/io/InputStream;

    move-result-object v0

    .line 71
    :goto_16
    new-instance v3, Lcom/holy/dash/Net$Resp;

    if-nez v0, :cond_2c

    const-string v0, ""

    :goto_1c
    invoke-direct {v3, v2, v0}, Lcom/holy/dash/Net$Resp;-><init>(ILjava/lang/String;)V
    :try_end_1f
    .catchall {:try_start_a .. :try_end_1f} :catchall_33

    .line 73
    if-eqz p3, :cond_23

    aput-object v6, p3, v5

    .line 74
    :cond_23
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 71
    return-object v3

    .line 70
    :cond_27
    :try_start_27
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object v0

    goto :goto_16

    .line 71
    :cond_2c
    const/high16 v4, 0x400000

    invoke-static {v0, v4}, Lcom/holy/dash/Net;->readAll(Ljava/io/InputStream;I)Ljava/lang/String;
    :try_end_31
    .catchall {:try_start_27 .. :try_end_31} :catchall_33

    move-result-object v0

    goto :goto_1c

    .line 73
    :catchall_33
    move-exception v0

    if-eqz p3, :cond_38

    aput-object v6, p3, v5

    .line 74
    :cond_38
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 75
    throw v0
.end method

.method static hex([B)Ljava/lang/String;
    .registers 9

    .prologue
    const/4 v1, 0x0

    .line 145
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    .line 146
    array-length v3, p0

    move v0, v1

    :goto_8
    if-ge v0, v3, :cond_23

    aget-byte v4, p0, v0

    sget-object v5, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    const-string v6, "%02x"

    const/4 v7, 0x1

    new-array v7, v7, [Ljava/lang/Object;

    invoke-static {v4}, Ljava/lang/Byte;->valueOf(B)Ljava/lang/Byte;

    move-result-object v4

    aput-object v4, v7, v1

    invoke-static {v5, v6, v7}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    add-int/lit8 v0, v0, 0x1

    goto :goto_8

    .line 147
    :cond_23
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method static normalize(Ljava/lang/String;)Ljava/lang/String;
    .registers 5

    .prologue
    const/4 v1, 0x0

    .line 29
    if-nez p0, :cond_5

    move-object v0, v1

    .line 38
    :goto_4
    return-object v0

    .line 30
    :cond_5
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    .line 31
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_11

    move-object v0, v1

    goto :goto_4

    .line 32
    :cond_11
    const-string v2, "(?i)^https?://.*"

    invoke-virtual {v0, v2}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_2c

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "http://"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 33
    :cond_2c
    invoke-static {v0}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v0

    .line 34
    invoke-virtual {v0}, Landroid/net/Uri;->getHost()Ljava/lang/String;

    move-result-object v2

    .line 35
    if-eqz v2, :cond_44

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_44

    const-string v3, "[A-Za-z0-9._\\-\\[\\]:]+"

    invoke-virtual {v2, v3}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v3

    if-nez v3, :cond_46

    :cond_44
    move-object v0, v1

    goto :goto_4

    .line 36
    :cond_46
    invoke-virtual {v0}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v1

    sget-object v3, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v1, v3}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v1

    .line 37
    invoke-virtual {v0}, Landroid/net/Uri;->getPort()I

    move-result v0

    .line 38
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v3, "://"

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    sget-object v3, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v2, v3}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    if-lez v0, :cond_8c

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, ":"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_82
    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    goto/16 :goto_4

    :cond_8c
    const-string v0, ""

    goto :goto_82
.end method

.method static open(Ljava/lang/String;Ljava/util/Map;I)Ljava/net/HttpURLConnection;
    .registers 7
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/util/Map",
            "<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;I)",
            "Ljava/net/HttpURLConnection;"
        }
    .end annotation

    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .prologue
    const/4 v2, 0x0

    .line 53
    new-instance v0, Ljava/net/URL;

    invoke-direct {v0, p0}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;

    move-result-object v0

    check-cast v0, Ljava/net/HttpURLConnection;

    .line 54
    const/16 v1, 0x3a98

    invoke-static {p2, v1}, Ljava/lang/Math;->min(II)I

    move-result v1

    invoke-virtual {v0, v1}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V

    .line 55
    invoke-virtual {v0, p2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V

    .line 56
    invoke-virtual {v0, v2}, Ljava/net/HttpURLConnection;->setInstanceFollowRedirects(Z)V

    .line 57
    invoke-virtual {v0, v2}, Ljava/net/HttpURLConnection;->setUseCaches(Z)V

    .line 58
    const-string v1, "User-Agent"

    const-string v2, "HolyApp/2.2"

    invoke-virtual {v0, v1, v2}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 59
    if-eqz p1, :cond_5d

    invoke-interface {p1}, Ljava/util/Map;->entrySet()Ljava/util/Set;

    move-result-object v1

    invoke-interface {v1}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :cond_2f
    :goto_2f
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_5d

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/util/Map$Entry;

    .line 60
    invoke-interface {v1}, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;

    move-result-object v2

    if-eqz v2, :cond_2f

    invoke-interface {v1}, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-nez v2, :cond_2f

    invoke-interface {v1}, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    invoke-interface {v1}, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    invoke-virtual {v0, v2, v1}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_2f

    .line 62
    :cond_5d
    return-object v0
.end method

.method static originOf(Ljava/lang/String;)Ljava/lang/String;
    .registers 2

    .prologue
    .line 44
    if-eqz p0, :cond_a

    :try_start_2
    const-string v0, "(?i)^https?://.*"

    invoke-virtual {p0, v0}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_d

    :cond_a
    const-string v0, ""

    .line 48
    :cond_c
    :goto_c
    return-object v0

    .line 45
    :cond_d
    invoke-static {p0}, Lcom/holy/dash/Net;->normalize(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 46
    if-nez v0, :cond_c

    const-string v0, ""
    :try_end_15
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_15} :catch_16

    goto :goto_c

    .line 47
    :catch_16
    move-exception v0

    .line 48
    const-string v0, ""

    goto :goto_c
.end method

.method static post(Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;I)Lcom/holy/dash/Net$Resp;
    .registers 9
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/util/Map",
            "<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;",
            "Ljava/lang/String;",
            "I)",
            "Lcom/holy/dash/Net$Resp;"
        }
    .end annotation

    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .prologue
    .line 80
    invoke-static {p0, p1, p3}, Lcom/holy/dash/Net;->open(Ljava/lang/String;Ljava/util/Map;I)Ljava/net/HttpURLConnection;

    move-result-object v1

    .line 82
    if-nez p2, :cond_8

    :try_start_6
    const-string p2, "{}"

    :cond_8
    const-string v0, "UTF-8"

    invoke-virtual {p2, v0}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v0

    .line 83
    const-string v2, "POST"

    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V

    .line 84
    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setDoOutput(Z)V

    .line 85
    const-string v2, "Content-Type"

    const-string v3, "application/json"

    invoke-virtual {v1, v2, v3}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 86
    array-length v2, v0

    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setFixedLengthStreamingMode(I)V

    .line 87
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getOutputStream()Ljava/io/OutputStream;
    :try_end_25
    .catchall {:try_start_6 .. :try_end_25} :catchall_4a

    move-result-object v2

    .line 88
    :try_start_26
    invoke-virtual {v2, v0}, Ljava/io/OutputStream;->write([B)V
    :try_end_29
    .catchall {:try_start_26 .. :try_end_29} :catchall_45

    :try_start_29
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    .line 89
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I

    move-result v2

    .line 90
    const/16 v0, 0x190

    if-lt v2, v0, :cond_4f

    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getErrorStream()Ljava/io/InputStream;

    move-result-object v0

    .line 91
    :goto_38
    new-instance v3, Lcom/holy/dash/Net$Resp;

    if-nez v0, :cond_54

    const-string v0, ""

    :goto_3e
    invoke-direct {v3, v2, v0}, Lcom/holy/dash/Net$Resp;-><init>(ILjava/lang/String;)V
    :try_end_41
    .catchall {:try_start_29 .. :try_end_41} :catchall_4a

    .line 93
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 91
    return-object v3

    .line 88
    :catchall_45
    move-exception v0

    :try_start_46
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    throw v0
    :try_end_4a
    .catchall {:try_start_46 .. :try_end_4a} :catchall_4a

    .line 93
    :catchall_4a
    move-exception v0

    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 94
    throw v0

    .line 90
    :cond_4f
    :try_start_4f
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object v0

    goto :goto_38

    .line 91
    :cond_54
    const/high16 v4, 0x10000

    invoke-static {v0, v4}, Lcom/holy/dash/Net;->readAll(Ljava/io/InputStream;I)Ljava/lang/String;
    :try_end_59
    .catchall {:try_start_4f .. :try_end_59} :catchall_4a

    move-result-object v0

    goto :goto_3e
.end method

.method static readAll(Ljava/io/InputStream;I)Ljava/lang/String;
    .registers 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .prologue
    .line 99
    :try_start_0
    new-instance v0, Ljava/io/ByteArrayOutputStream;

    invoke-direct {v0}, Ljava/io/ByteArrayOutputStream;-><init>()V

    .line 100
    const/16 v1, 0x2000

    new-array v1, v1, [B

    .line 102
    :cond_9
    invoke-virtual {p0, v1}, Ljava/io/InputStream;->read([B)I

    move-result v2

    if-lez v2, :cond_26

    .line 103
    const/4 v3, 0x0

    invoke-virtual {v0, v1, v3, v2}, Ljava/io/ByteArrayOutputStream;->write([BII)V

    .line 104
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->size()I

    move-result v2

    if-le v2, p1, :cond_9

    new-instance v0, Ljava/io/IOException;

    const-string v1, "response too big"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_21
    .catchall {:try_start_0 .. :try_end_21} :catchall_21

    .line 108
    :catchall_21
    move-exception v0

    invoke-virtual {p0}, Ljava/io/InputStream;->close()V

    .line 109
    throw v0

    .line 106
    :cond_26
    :try_start_26
    new-instance v1, Ljava/lang/String;

    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object v0

    const-string v2, "UTF-8"

    invoke-direct {v1, v0, v2}, Ljava/lang/String;-><init>([BLjava/lang/String;)V
    :try_end_31
    .catchall {:try_start_26 .. :try_end_31} :catchall_21

    .line 108
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V

    .line 106
    return-object v1
.end method
