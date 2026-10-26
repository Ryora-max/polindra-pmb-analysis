# Key metrics POLINDRA (dihitung otomatis dari data)

- Pendaftar 17,900 | Mahasiswa 6,278 | KHS 27,013
- Pendaftar 1,400 -> 3,800 (+171%); lulus seleksi 57.7% -> 31.9%; kursi lulus 808 -> 1,214 (+50%)
- Yield daftar ulang (lulus -> registrasi): Mandiri 77.4%, SNBP 88.0%, SBMPN 88.4%, SNBT 88.8%, Prestasi 88.9%, SNMPN 89.1%
- ANOVA IPK ~ jalur: F=14.9, p=1.5e-14, eta^2=0.012
- Mahasiswa per jalur: SBMPN 1,747, Mandiri 1,744, SNMPN 1,321, SNBT 863, SNBP 426, Prestasi 177
- Kab. Indramayu 34.4% | Ciayumajakuning (5 wilayah) 68.0%
- Dropout rate 7.2%; 65% DO berhenti dalam 2 semester pertama
- Rata IP sem-1: DO 3.15 vs non-DO 3.34
- Aturan IP1<2.5: flag 1% mhs, recall 5%, precision 26.1%, lift 3.63x
- Aturan IP1<3.0: flag 19% mhs, recall 33%, precision 12.4%, lift 1.72x
- Aturan IP1<3.2: flag 36% mhs, recall 52%, precision 10.6%, lift 1.47x
- Logit DO (p<0.05): ip1 OR=0.22; C(jenis_sekolah)[T.MA] OR=0.49; C(jenis_sekolah)[T.SMK] OR=0.55; C(jurusan)[T.Teknik] OR=0.59; C(jurusan)[T.Teknik Informatika] OR=0.70
- Random Forest DO ROC-AUC 5-fold CV: 0.62 +- 0.02
