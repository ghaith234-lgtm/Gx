import com.android.apksig.ApkSigner;
import com.android.apksig.ApkVerifier;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

/**
 * 📱 Signs / verifies the Holy app with apksig — APK Signature Scheme v2 (the app needs Android 7.0+, which reads v2;
 * apksig 2.3.0's v1 path needs JDK internals that newer JDKs removed).
 *   sign   IN.apk OUT.apk KEY.p12   — the password comes from the environment variable HOLY_KEY_PASS, never from the command line
 *   verify APK                      — prints v1 / v2 and the signing certificate's sha256
 * The key file itself never enters the repository (it is public).
 */
public final class Sign {
    private static String hex(byte[] b) {
        StringBuilder s = new StringBuilder();
        for (byte x : b) s.append(String.format("%02x", x & 0xff));
        return s.toString();
    }

    public static void main(String[] a) throws Exception {
        if (a.length == 4 && a[0].equals("sign")) {
            String pw = System.getenv("HOLY_KEY_PASS");
            if (pw == null || pw.isEmpty()) throw new IllegalStateException("HOLY_KEY_PASS is not set");
            char[] p = pw.toCharArray();
            KeyStore ks = KeyStore.getInstance("PKCS12");
            try (InputStream in = new FileInputStream(a[3])) {
                ks.load(in, p);
            }
            String alias = null;
            for (Enumeration<String> e = ks.aliases(); e.hasMoreElements(); ) {
                String x = e.nextElement();
                if (ks.isKeyEntry(x)) {
                    alias = x;
                    break;
                }
            }
            if (alias == null) throw new IllegalStateException("no key in the key file");
            PrivateKey key = (PrivateKey) ks.getKey(alias, p);
            List<X509Certificate> chain = new ArrayList<>();
            for (Certificate c : ks.getCertificateChain(alias)) chain.add((X509Certificate) c);
            ApkSigner.SignerConfig sc = new ApkSigner.SignerConfig.Builder("HOLY", key, chain).build();
            new ApkSigner.Builder(Collections.singletonList(sc))
                    .setInputApk(new File(a[1]))
                    .setOutputApk(new File(a[2]))
                    .setMinSdkVersion(24)
                    .setV1SigningEnabled(false)
                    .setV2SigningEnabled(true)
                    .build()
                    .sign();
            System.out.println("signed " + a[2]);
            return;
        }
        if (a.length == 2 && a[0].equals("verify")) {
            ApkVerifier.Result r = new ApkVerifier.Builder(new File(a[1])).build().verify();
            System.out.println("verified=" + r.isVerified() + " v1=" + r.isVerifiedUsingV1Scheme() + " v2=" + r.isVerifiedUsingV2Scheme());
            for (X509Certificate c : r.getSignerCertificates()) {
                System.out.println("cert_sha256=" + hex(MessageDigest.getInstance("SHA-256").digest(c.getEncoded())));
            }
            for (ApkVerifier.IssueWithParams i : r.getErrors()) System.out.println("error: " + i);
            System.exit(r.isVerified() ? 0 : 1);
        }
        System.err.println("usage: Sign sign IN OUT KEY.p12 | Sign verify APK");
        System.exit(2);
    }
}
