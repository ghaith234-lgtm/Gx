.class final Lcom/holy/dash/Oem;
.super Ljava/lang/Object;
.source "Oem.java"


# static fields
.field private static final PAGES:[[Ljava/lang/String;


# direct methods
.method static constructor <clinit>()V
    .registers 7

    .prologue
    const/4 v6, 0x2

    const/4 v5, 0x1

    const/4 v4, 0x0

    .line 30
    const/16 v0, 0x12

    new-array v0, v0, [[Ljava/lang/String;

    new-array v1, v6, [Ljava/lang/String;

    const-string v2, "com.miui.securitycenter"

    aput-object v2, v1, v4

    const-string v2, "com.miui.permcenter.autostart.AutoStartManagementActivity"

    aput-object v2, v1, v5

    aput-object v1, v0, v4

    new-array v1, v6, [Ljava/lang/String;

    const-string v2, "com.coloros.safecenter"

    aput-object v2, v1, v4

    const-string v2, "com.coloros.safecenter.permission.startup.StartupAppListActivity"

    aput-object v2, v1, v5

    aput-object v1, v0, v5

    new-array v1, v6, [Ljava/lang/String;

    const-string v2, "com.coloros.safecenter"

    aput-object v2, v1, v4

    const-string v2, "com.coloros.safecenter.startupapp.StartupAppListActivity"

    aput-object v2, v1, v5

    aput-object v1, v0, v6

    const/4 v1, 0x3

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.oppo.safe"

    aput-object v3, v2, v4

    const-string v3, "com.oppo.safe.permission.startup.StartupAppListActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/4 v1, 0x4

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.oplus.battery"

    aput-object v3, v2, v4

    const-string v3, "com.oplus.powermanager.fuelgaue.PowerUsageModelActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/4 v1, 0x5

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.vivo.permissionmanager"

    aput-object v3, v2, v4

    const-string v3, "com.vivo.permissionmanager.activity.BgStartUpManagerActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/4 v1, 0x6

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.iqoo.secure"

    aput-object v3, v2, v4

    const-string v3, "com.iqoo.secure.ui.phoneoptimize.BgStartUpManager"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/4 v1, 0x7

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.iqoo.secure"

    aput-object v3, v2, v4

    const-string v3, "com.iqoo.secure.ui.phoneoptimize.AddWhiteListActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0x8

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.huawei.systemmanager"

    aput-object v3, v2, v4

    const-string v3, "com.huawei.systemmanager.startupmgr.ui.StartupNormalAppListActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0x9

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.huawei.systemmanager"

    aput-object v3, v2, v4

    const-string v3, "com.huawei.systemmanager.optimize.process.ProtectActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xa

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.hihonor.systemmanager"

    aput-object v3, v2, v4

    const-string v3, "com.hihonor.systemmanager.startupmgr.ui.StartupNormalAppListActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xb

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.transsion.phonemaster"

    aput-object v3, v2, v4

    const-string v3, "com.cyin.himgr.autostart.AutoStartActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xc

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.oneplus.security"

    aput-object v3, v2, v4

    const-string v3, "com.oneplus.security.chainlaunch.view.ChainLaunchAppListActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xd

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.asus.mobilemanager"

    aput-object v3, v2, v4

    const-string v3, "com.asus.mobilemanager.autostart.AutoStartActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xe

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.letv.android.letvsafe"

    aput-object v3, v2, v4

    const-string v3, "com.letv.android.letvsafe.AutobootManageActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0xf

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.evenwell.powersaving.g3"

    aput-object v3, v2, v4

    const-string v3, "com.evenwell.powersaving.g3.exception.PowerSaverExceptionActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0x10

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.samsung.android.lool"

    aput-object v3, v2, v4

    const-string v3, "com.samsung.android.sm.ui.battery.BatteryActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    const/16 v1, 0x11

    new-array v2, v6, [Ljava/lang/String;

    const-string v3, "com.samsung.android.sm"

    aput-object v3, v2, v4

    const-string v3, "com.samsung.android.sm.ui.battery.BatteryActivity"

    aput-object v3, v2, v5

    aput-object v2, v0, v1

    sput-object v0, Lcom/holy/dash/Oem;->PAGES:[[Ljava/lang/String;

    return-void
.end method

.method private constructor <init>()V
    .registers 1

    .prologue
    .line 17
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static maker()Ljava/lang/String;
    .registers 2

    .prologue
    .line 19
    sget-object v0, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    if-nez v0, :cond_d

    const-string v0, ""

    :goto_6
    sget-object v1, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v0, v1}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v0

    return-object v0

    :cond_d
    sget-object v0, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    goto :goto_6
.end method

.method static open(Landroid/app/Activity;)Ljava/lang/String;
    .registers 11

    .prologue
    const/4 v1, 0x0

    .line 53
    invoke-static {}, Lcom/holy/dash/Oem;->maker()Ljava/lang/String;

    move-result-object v2

    .line 54
    sget-object v3, Lcom/holy/dash/Oem;->PAGES:[[Ljava/lang/String;

    array-length v4, v3

    move v0, v1

    :goto_9
    if-ge v0, v4, :cond_40

    aget-object v5, v3, v0

    .line 55
    const-string v6, "samsung"

    invoke-virtual {v2, v6}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v6

    aget-object v7, v5, v1

    const-string v8, "com.samsung"

    invoke-virtual {v7, v8}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v7

    if-eq v6, v7, :cond_20

    .line 54
    :goto_1d
    add-int/lit8 v0, v0, 0x1

    goto :goto_9

    .line 57
    :cond_20
    :try_start_20
    new-instance v6, Landroid/content/Intent;

    invoke-direct {v6}, Landroid/content/Intent;-><init>()V

    new-instance v7, Landroid/content/ComponentName;

    const/4 v8, 0x0

    aget-object v8, v5, v8

    const/4 v9, 0x1

    aget-object v5, v5, v9

    invoke-direct {v7, v8, v5}, Landroid/content/ComponentName;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v6, v7}, Landroid/content/Intent;->setComponent(Landroid/content/ComponentName;)Landroid/content/Intent;

    move-result-object v5

    const/high16 v6, 0x10000000

    invoke-virtual {v5, v6}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v5

    invoke-virtual {p0, v5}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V

    .line 58
    const-string v0, "oem"
    :try_end_3f
    .catch Ljava/lang/Exception; {:try_start_20 .. :try_end_3f} :catch_72

    .line 68
    :goto_3f
    return-object v0

    .line 64
    :cond_40
    :try_start_40
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.APPLICATION_DETAILS_SETTINGS"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "package:"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {p0}, Landroid/app/Activity;->getPackageName()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v2

    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    const/high16 v1, 0x10000000

    .line 65
    invoke-virtual {v0, v1}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v0

    .line 64
    invoke-virtual {p0, v0}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V

    .line 66
    const-string v0, "app"
    :try_end_6d
    .catch Ljava/lang/Exception; {:try_start_40 .. :try_end_6d} :catch_6e

    goto :goto_3f

    .line 67
    :catch_6e
    move-exception v0

    .line 68
    const-string v0, ""

    goto :goto_3f

    .line 59
    :catch_72
    move-exception v5

    goto :goto_1d
.end method

.method static strict()Z
    .registers 7

    .prologue
    const/4 v0, 0x1

    const/4 v1, 0x0

    .line 23
    invoke-static {}, Lcom/holy/dash/Oem;->maker()Ljava/lang/String;

    move-result-object v3

    .line 24
    const/16 v2, 0x16

    new-array v4, v2, [Ljava/lang/String;

    const-string v2, "xiaomi"

    aput-object v2, v4, v1

    const-string v2, "redmi"

    aput-object v2, v4, v0

    const/4 v2, 0x2

    const-string v5, "poco"

    aput-object v5, v4, v2

    const/4 v2, 0x3

    const-string v5, "oppo"

    aput-object v5, v4, v2

    const/4 v2, 0x4

    const-string v5, "realme"

    aput-object v5, v4, v2

    const/4 v2, 0x5

    const-string v5, "oneplus"

    aput-object v5, v4, v2

    const/4 v2, 0x6

    const-string v5, "vivo"

    aput-object v5, v4, v2

    const/4 v2, 0x7

    const-string v5, "iqoo"

    aput-object v5, v4, v2

    const/16 v2, 0x8

    const-string v5, "huawei"

    aput-object v5, v4, v2

    const/16 v2, 0x9

    const-string v5, "honor"

    aput-object v5, v4, v2

    const/16 v2, 0xa

    const-string v5, "samsung"

    aput-object v5, v4, v2

    const/16 v2, 0xb

    const-string v5, "infinix"

    aput-object v5, v4, v2

    const/16 v2, 0xc

    const-string v5, "tecno"

    aput-object v5, v4, v2

    const/16 v2, 0xd

    const-string v5, "itel"

    aput-object v5, v4, v2

    const/16 v2, 0xe

    const-string v5, "transsion"

    aput-object v5, v4, v2

    const/16 v2, 0xf

    const-string v5, "asus"

    aput-object v5, v4, v2

    const/16 v2, 0x10

    const-string v5, "meizu"

    aput-object v5, v4, v2

    const/16 v2, 0x11

    const-string v5, "nokia"

    aput-object v5, v4, v2

    const/16 v2, 0x12

    const-string v5, "hmd"

    aput-object v5, v4, v2

    const/16 v2, 0x13

    const-string v5, "lenovo"

    aput-object v5, v4, v2

    const/16 v2, 0x14

    const-string v5, "letv"

    aput-object v5, v4, v2

    const/16 v2, 0x15

    const-string v5, "leeco"

    aput-object v5, v4, v2

    array-length v5, v4

    move v2, v1

    :goto_86
    if-ge v2, v5, :cond_94

    aget-object v6, v4, v2

    .line 26
    invoke-virtual {v3, v6}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v6

    if-eqz v6, :cond_91

    .line 27
    :goto_90
    return v0

    .line 24
    :cond_91
    add-int/lit8 v2, v2, 0x1

    goto :goto_86

    :cond_94
    move v0, v1

    .line 27
    goto :goto_90
.end method
