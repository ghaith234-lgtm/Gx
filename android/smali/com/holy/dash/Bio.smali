.class final Lcom/holy/dash/Bio;
.super Ljava/lang/Object;
.source "Bio.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/holy/dash/Bio$Done;
    }
.end annotation


# direct methods
.method private constructor <init>()V
    .registers 1

    .prologue
    .line 13
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static ask(Landroid/app/Activity;Ljava/lang/String;Lcom/holy/dash/Bio$Done;)V
    .registers 7

    .prologue
    .line 39
    new-instance v0, Landroid/hardware/biometrics/BiometricPrompt$Builder;

    invoke-direct {v0, p0}, Landroid/hardware/biometrics/BiometricPrompt$Builder;-><init>(Landroid/content/Context;)V

    const-string v1, "Holy"

    invoke-virtual {v0, v1}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/hardware/biometrics/BiometricPrompt$Builder;

    move-result-object v0

    invoke-virtual {v0, p1}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->setSubtitle(Ljava/lang/CharSequence;)Landroid/hardware/biometrics/BiometricPrompt$Builder;

    move-result-object v0

    .line 40
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1e

    if-lt v1, v2, :cond_31

    .line 41
    const v1, 0x80ff

    invoke-virtual {v0, v1}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->setAllowedAuthenticators(I)Landroid/hardware/biometrics/BiometricPrompt$Builder;

    .line 49
    :goto_1b
    invoke-virtual {v0}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->build()Landroid/hardware/biometrics/BiometricPrompt;

    move-result-object v0

    new-instance v1, Landroid/os/CancellationSignal;

    invoke-direct {v1}, Landroid/os/CancellationSignal;-><init>()V

    invoke-virtual {p0}, Landroid/app/Activity;->getMainExecutor()Ljava/util/concurrent/Executor;

    move-result-object v2

    new-instance v3, Lcom/holy/dash/Bio$2;

    invoke-direct {v3, p2}, Lcom/holy/dash/Bio$2;-><init>(Lcom/holy/dash/Bio$Done;)V

    invoke-virtual {v0, v1, v2, v3}, Landroid/hardware/biometrics/BiometricPrompt;->authenticate(Landroid/os/CancellationSignal;Ljava/util/concurrent/Executor;Landroid/hardware/biometrics/BiometricPrompt$AuthenticationCallback;)V

    .line 57
    return-void

    .line 42
    :cond_31
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1d

    if-ne v1, v2, :cond_3c

    .line 43
    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->setDeviceCredentialAllowed(Z)Landroid/hardware/biometrics/BiometricPrompt$Builder;

    goto :goto_1b

    .line 45
    :cond_3c
    const-string v1, "\u0631\u0645\u0632 \u0627\u0644\u0645\u0648\u0628\u0627\u064a\u0644"

    invoke-virtual {p0}, Landroid/app/Activity;->getMainExecutor()Ljava/util/concurrent/Executor;

    move-result-object v2

    new-instance v3, Lcom/holy/dash/Bio$1;

    invoke-direct {v3, p2}, Lcom/holy/dash/Bio$1;-><init>(Lcom/holy/dash/Bio$Done;)V

    invoke-virtual {v0, v1, v2, v3}, Landroid/hardware/biometrics/BiometricPrompt$Builder;->setNegativeButton(Ljava/lang/CharSequence;Ljava/util/concurrent/Executor;Landroid/content/DialogInterface$OnClickListener;)Landroid/hardware/biometrics/BiometricPrompt$Builder;

    goto :goto_1b
.end method

.method static has(Landroid/content/Context;)Z
    .registers 3

    .prologue
    .line 27
    :try_start_0
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1d

    if-lt v0, v1, :cond_1b

    .line 28
    const-string v0, "biometric"

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/hardware/biometrics/BiometricManager;

    .line 29
    if-eqz v0, :cond_18

    invoke-virtual {v0}, Landroid/hardware/biometrics/BiometricManager;->canAuthenticate()I
    :try_end_13
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_13} :catch_1a

    move-result v0

    if-nez v0, :cond_18

    const/4 v0, 0x1

    .line 34
    :goto_17
    return v0

    .line 29
    :cond_18
    const/4 v0, 0x0

    goto :goto_17

    .line 31
    :catch_1a
    move-exception v0

    .line 34
    :cond_1b
    invoke-virtual {p0}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    const-string v1, "android.hardware.fingerprint"

    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->hasSystemFeature(Ljava/lang/String;)Z

    move-result v0

    goto :goto_17
.end method
