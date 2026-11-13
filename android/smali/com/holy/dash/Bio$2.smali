.class Lcom/holy/dash/Bio$2;
.super Landroid/hardware/biometrics/BiometricPrompt$AuthenticationCallback;
.source "Bio.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Bio;->ask(Landroid/app/Activity;Ljava/lang/String;Lcom/holy/dash/Bio$Done;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$d:Lcom/holy/dash/Bio$Done;


# direct methods
.method constructor <init>(Lcom/holy/dash/Bio$Done;)V
    .registers 2

    .prologue
    .line 49
    iput-object p1, p0, Lcom/holy/dash/Bio$2;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-direct {p0}, Landroid/hardware/biometrics/BiometricPrompt$AuthenticationCallback;-><init>()V

    return-void
.end method


# virtual methods
.method public onAuthenticationError(ILjava/lang/CharSequence;)V
    .registers 4

    .prologue
    .line 53
    const/16 v0, 0xa

    if-eq p1, v0, :cond_7

    const/4 v0, 0x5

    if-ne p1, v0, :cond_d

    :cond_7
    iget-object v0, p0, Lcom/holy/dash/Bio$2;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-interface {v0}, Lcom/holy/dash/Bio$Done;->cancelled()V

    .line 55
    :cond_c
    :goto_c
    return-void

    .line 54
    :cond_d
    const/16 v0, 0xd

    if-eq p1, v0, :cond_c

    iget-object v0, p0, Lcom/holy/dash/Bio$2;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-interface {v0}, Lcom/holy/dash/Bio$Done;->fallback()V

    goto :goto_c
.end method

.method public onAuthenticationSucceeded(Landroid/hardware/biometrics/BiometricPrompt$AuthenticationResult;)V
    .registers 3

    .prologue
    .line 50
    iget-object v0, p0, Lcom/holy/dash/Bio$2;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-interface {v0}, Lcom/holy/dash/Bio$Done;->ok()V

    return-void
.end method
