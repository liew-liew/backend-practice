# test_hash.py
from auth import get_password_hash, verify_password

if __name__ == "__main__":
    print("🧪 测试 auth.py...")
    
    # 1. 哈希密码
    pwd = "hello123"
    hashed = get_password_hash(pwd)
    print("✅ 哈希成功:", hashed[:20] + "...")

    # 2. 验证正确密码
    assert verify_password(pwd, hashed), "❌ 验证失败！"
    print("✅ 正确密码验证通过")

    # 3. 验证错误密码
    assert not verify_password("wrong", hashed), "❌ 错误密码应被拒绝！"
    print("✅ 错误密码被拒绝")

    print("🎉 auth.py 工作正常！")