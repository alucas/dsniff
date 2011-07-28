#include "Python.h"

#include <stdlib.h>
#include <stdio.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <dlfcn.h>

#define SOCKET 8

typedef ssize_t (* send_t)(int sockfd, const void *buf, size_t len, int flags);
typedef ssize_t (* recv_t)(int sockfd,       void *buf, size_t len, int flags);
typedef int (* connect_t)(int sockfd, const struct sockaddr *addr,
		                   socklen_t addrlen);

static send_t newsend = NULL;
static recv_t newrecv = NULL;
static connect_t newconnect = NULL;

static PyObject* pinst = NULL;

static int initVars(void){
	char *msg;

	/* init error */
	dlerror();

	printf("[init newconnect]\n");

	newconnect = (connect_t)dlsym(RTLD_NEXT, "connect");
	if((msg = dlerror()) != NULL){
		fprintf(stderr, "Error : init newconnect");
		return -1;
	}

	printf("[init newsend]\n");

	newsend = (send_t)dlsym(RTLD_NEXT, "send");
	if((msg = dlerror()) != NULL){
		fprintf(stderr, "Error : init newsend %s\n", msg);
		return -1;
	}

	printf("[init newrecv]\n");

	newrecv = (recv_t)dlsym(RTLD_NEXT, "recv");
	if((msg = dlerror()) != NULL){
		fprintf(stderr, "Error : init newrecv %s\n", msg);
		return -1;
	}

	printf("[init python]\n");

	Py_Initialize();

	printf("[init python modules]\n");

	/* run objects with low-level calls */
	PyObject *pmod, *pclass;

	/* instance = module.klass( ) */
	pmod = PyImport_ImportModule("dofussniff.main");
	if(pmod != NULL){
		pclass = PyObject_GetAttrString(pmod, "DofusSniff");
		if(pclass != NULL){
			pinst  = PyEval_CallObject(pclass, NULL);
			if(pinst == NULL){
				PyErr_Print();
				return -1;
			}

			Py_DECREF(pclass);
		}else{
			PyErr_Print();
			return -1;
		}

		Py_DECREF(pmod);
	}else{
		PyErr_Print();
		return -1;
	}

	printf("[init: All good!]\n");

	return 0;
}

extern ssize_t send(int sockfd, const void *buf, size_t len, int flags){
	if(newsend == NULL){
		if(initVars()){
			fprintf(stderr, "init failure\n");
			exit(EXIT_FAILURE);
		}
	}

	return newsend(sockfd, buf, len, flags);
}

extern ssize_t recv(int sockfd, void *buf, size_t len, int flags){
	if(newrecv == NULL){
		if(initVars()){
			fprintf(stderr, "init failure\n");
			exit(EXIT_FAILURE);
		}
	}

	ssize_t msglen;
	msglen = newrecv(sockfd, buf, len, flags);
	
	if(sockfd == SOCKET && pinst != NULL){
		PyObject *pmeth, *pargs, *pres;

		pmeth  = PyObject_GetAttrString(pinst, "decode");
		if(pmeth != NULL){
			pargs  = Py_BuildValue("(s#)", buf, msglen);
			if(pargs != NULL){
				pres = PyEval_CallObject(pmeth, pargs);
				if(pres != NULL){
					Py_DECREF(pres);
				}else{
					PyErr_Print();
				}

				Py_DECREF(pmeth);
			}else{
				PyErr_Print();
			}

			Py_DECREF(pargs);
		}else{
			PyErr_Print();
		}
	}else{
		printf("socket: %d\n", sockfd);
	}

	return msglen;
}

extern int connect(int sockfd, const struct sockaddr *addr,
		                   socklen_t addrlen){
	if(newconnect == NULL){
		if(initVars()){
			fprintf(stderr, "init failure\n");
			exit(EXIT_FAILURE);
		}
	}

	int ret = newconnect(sockfd, addr, addrlen);

	return ret;
}
