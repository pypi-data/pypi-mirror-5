**To update the password for an IAM user**

The following ``update-login-profile`` commmand creates a new password for the IAM user named ``Bob``::

  aws iam update-login-profile --user-name Bob --password <password>

Output::

  {
      "ResponseMetadata": {
          "RequestId": "b9cd3e32-4a54-11e2-8110-65075b2814da"
      }
  }    

To set a password policy for the account, use the ``update-account-password-policy`` command. If the new password violates the account password policy, the command returns a ``PasswordPolicyViolation`` error.

If the account password policy allows them to, IAM users can change their own passwords using the ``change-password`` command.

For more information, see `Managing Passwords`_ in the *Using IAM* guide.
 
.. _Managing Passwords: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingLogins.html


